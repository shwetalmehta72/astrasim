from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

import asyncpg

from app.clients.polygon_options import PolygonOptionsClient, PolygonOptionsClientError
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.connection import get_pool
from app.services.options import cache, degraded_mode, refresh_policy

logger = get_logger("options.atm")


async def ingest_atm_straddle(
    symbol: str,
    target_date: Optional[date] = None,
    *,
    client: Optional[PolygonOptionsClient] = None,
    settings: Optional[Settings] = None,
    force: bool = False,
) -> Dict[str, Any]:
    target_date = target_date or date.today()
    settings = settings or get_settings()
    pool = await get_pool()
    owns_client = client is None
    if client is None:
        client = PolygonOptionsClient(settings=settings)

    async with pool.acquire() as conn:
        run_id = await _create_ingestion_run(conn)
        try:
            security_id = await _get_security_id(conn, symbol)
            underlying_price = await get_underlying_price(conn, security_id, target_date)
            if underlying_price is None:
                raise ValueError(f"No underlying price found for {symbol}")

            cached_atm = cache.get_cached_atm(symbol, settings=settings) if not force else None
            if (
                cached_atm
                and not refresh_policy.should_refresh_atm(symbol, underlying_price, settings=settings, force=force)
            ):
                payload = dict(cached_atm.value)
                payload["cached"] = True
                return payload

            expirations = await client.fetch_expirations(symbol)
            expiration = _select_expiration(
                expirations,
                target_date,
                settings.OPTIONS_MIN_DTE_BUFFER,
            )
            if expiration is None:
                raise ValueError("No valid expirations returned from Polygon")

            expiration_key = expiration.isoformat()

            cached_chain_entry = cache.get_cached_chain(symbol, expiration_key, settings=settings) if not force else None
            chain = None
            chain_source = "live"

            if (
                cached_chain_entry
                and not refresh_policy.should_refresh_chain(symbol, expiration_key, settings=settings, force=force)
            ):
                chain = cached_chain_entry.value
                chain_source = cached_chain_entry.metadata.get("source", "cache")

            if chain is None:
                try:
                    chain = await client.fetch_chain(symbol, expiration)
                    chain_source = "live"
                    cache.set_cached_chain(
                        symbol,
                        expiration_key,
                        chain,
                        {"source": chain_source},
                        settings=settings,
                    )
                    refresh_policy.record_chain_refresh(symbol, expiration_key)
                except PolygonOptionsClientError:
                    if cached_chain_entry:
                        chain = cached_chain_entry.value
                        chain_source = "cache"
                    else:
                        fallback = await degraded_mode.fallback_chain_from_snapshot(conn, security_id, expiration)
                        if fallback is None:
                            raise
                        chain = fallback
                        chain_source = "historical"

            if not chain:
                raise ValueError("Polygon returned empty option chain")

            await _insert_option_chain(conn, security_id, chain)
            straddle_payload = _build_atm_straddle(
                chain,
                underlying_price,
                expiration,
                target_date,
            )
            straddle_payload["metadata"] = {
                "chain_source": chain_source,
                "degraded": chain_source != "live",
            }

            straddle_id = await _insert_straddle(
                conn,
                security_id,
                straddle_payload,
                run_id,
            )
            await _complete_run(conn, run_id, 1)
            straddle_payload["id"] = straddle_id
            straddle_payload["symbol"] = symbol.upper()
            cache.set_cached_atm(
                symbol,
                straddle_payload,
                {"underlying_price": underlying_price, "source": chain_source},
                settings=settings,
            )
            refresh_policy.record_atm_refresh(symbol, underlying_price)
            return straddle_payload
        except Exception as exc:  # noqa: BLE001
            logger.exception("ATM straddle ingestion failed for %s: %s", symbol, exc)
            await _fail_run(conn, run_id, exc, {"symbol": symbol.upper()})
            raise
        finally:
            if owns_client:
                await client.close()


async def get_recent_atm_straddles(symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        security_id = await _get_security_id(conn, symbol)
        rows = await conn.fetch(
            """
            SELECT expiration,
                   strike,
                   call_mid,
                   put_mid,
                   straddle_mid,
                   implied_vol,
                   dte,
                   snapshot_timestamp
            FROM option_straddles
            WHERE security_id=$1
            ORDER BY snapshot_timestamp DESC
            LIMIT $2
            """,
            security_id,
            limit,
        )
        return [
            {
                "symbol": symbol.upper(),
                "expiration": row["expiration"],
                "strike": float(row["strike"]),
                "call_mid": row["call_mid"],
                "put_mid": row["put_mid"],
                "straddle_mid": row["straddle_mid"],
                "implied_vol": row["implied_vol"],
                "dte": row["dte"],
                "snapshot_timestamp": row["snapshot_timestamp"],
            }
            for row in rows
        ]


async def _get_security_id(conn: asyncpg.Connection, symbol: str) -> int:
    security_id = await conn.fetchval(
        "SELECT id FROM securities WHERE symbol=$1 LIMIT 1",
        symbol.upper(),
    )
    if security_id is None:
        raise ValueError(f"Security {symbol} not found in securities table")
    return int(security_id)


async def get_underlying_price(
    conn: asyncpg.Connection,
    security_id: int,
    target_date: date,
) -> Optional[float]:
    price = await conn.fetchval(
        """
        SELECT close
        FROM ohlcv_bars
        WHERE security_id=$1 AND interval='1d' AND time <= $2
        ORDER BY time DESC
        LIMIT 1
        """,
        security_id,
        datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc),
    )
    return float(price) if price is not None else None


def _select_expiration(
    expirations: Iterable[date],
    target_date: date,
    min_buffer_days: int,
) -> Optional[date]:
    min_expiration_date = target_date + timedelta(days=min_buffer_days)
    future = [exp for exp in expirations if exp >= min_expiration_date]
    if future:
        return min(future)
    if expirations:
        return min(expirations)
    return None


def _build_atm_straddle(
    chain: List[Dict[str, Any]],
    underlying_price: float,
    expiration: date,
    target_date: date,
) -> Dict[str, Any]:
    grouped: Dict[float, Dict[str, Dict[str, Any]]] = {}
    for option in chain:
        strike = option["strike"]
        grouped.setdefault(strike, {})
        grouped[strike][option["call_put"]] = option

    best: Optional[Tuple[float, Dict[str, Any], Dict[str, Any]]] = None
    best_diff: Optional[float] = None
    for strike, legs in grouped.items():
        call = legs.get("call")
        put = legs.get("put")
        if not call or not put:
            continue
        diff = abs(strike - underlying_price)
        if best is None or diff < best_diff:  # type: ignore[arg-type]
            best = (strike, call, put)
            best_diff = diff

    if not best:
        raise ValueError("Unable to find matching ATM call/put pair")

    strike, call_leg, put_leg = best

    call_mid = call_leg["mid"]
    put_mid = put_leg["mid"]
    if call_mid is None:
        call_mid = _safe_mid(call_leg["bid"], call_leg["ask"])
    if put_mid is None:
        put_mid = _safe_mid(put_leg["bid"], put_leg["ask"])
    if call_mid is None or put_mid is None:
        raise ValueError("Unable to compute mid prices for ATM legs")

    straddle_mid = call_mid + put_mid
    dte = max((expiration - target_date).days, 1)
    implied_vol = calculate_iv_proxy(straddle_mid, underlying_price, dte)

    snapshot_ts = datetime.now(tz=timezone.utc)

    return {
        "strike": strike,
        "expiration": expiration,
        "call_mid": call_mid,
        "put_mid": put_mid,
        "straddle_mid": straddle_mid,
        "implied_vol": implied_vol,
        "dte": dte,
        "snapshot_timestamp": snapshot_ts,
        "raw_call": call_leg["raw"],
        "raw_put": put_leg["raw"],
    }


def _safe_mid(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
    if bid is None or ask is None:
        return None
    return (bid + ask) / 2


def calculate_iv_proxy(straddle_mid: float, underlying_price: float, dte: int) -> Optional[float]:
    if underlying_price <= 0 or dte <= 0:
        return None
    try:
        return straddle_mid / (underlying_price * math.sqrt(dte / 365))
    except ZeroDivisionError:
        return None


async def _insert_option_chain(
    conn: asyncpg.Connection,
    security_id: int,
    chain: List[Dict[str, Any]],
) -> None:
    rows = [
        (
            security_id,
            option["option_symbol"],
            option["strike"],
            option["expiration"],
            option["call_put"],
            option["bid"],
            option["ask"],
            option["mid"],
            option["volume"],
            option["open_interest"],
            option["underlying_price"],
            option["raw"],
        )
        for option in chain
    ]
    await conn.executemany(
        """
        INSERT INTO option_chain_raw (
            security_id,
            option_symbol,
            strike,
            expiration,
            call_put,
            bid,
            ask,
            mid,
            volume,
            open_interest,
            underlying_price,
            raw_payload
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
        """,
        rows,
    )


async def _insert_straddle(
    conn: asyncpg.Connection,
    security_id: int,
    payload: Dict[str, Any],
    run_id: int,
) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO option_straddles (
            security_id,
            expiration,
            strike,
            call_mid,
            put_mid,
            straddle_mid,
            implied_vol,
            dte,
            snapshot_timestamp,
            ingestion_run_id,
            raw_call,
            raw_put
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
        RETURNING id
        """,
        security_id,
        payload["expiration"],
        payload["strike"],
        payload["call_mid"],
        payload["put_mid"],
        payload["straddle_mid"],
        payload["implied_vol"],
        payload["dte"],
        payload["snapshot_timestamp"],
        run_id,
        payload["raw_call"],
        payload["raw_put"],
    )
    return int(row["id"])


async def _create_ingestion_run(conn: asyncpg.Connection) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO ingestion_runs (source, target_table, status)
        VALUES ('options_atm_straddle', 'option_straddles', 'running')
        RETURNING id
        """
    )
    return int(row["id"])


async def _complete_run(conn: asyncpg.Connection, run_id: int, rows_inserted: int) -> None:
    await conn.execute(
        """
        UPDATE ingestion_runs
        SET status='success', finished_at=NOW(), rows_inserted=$2
        WHERE id=$1
        """,
        run_id,
        rows_inserted,
    )


async def _fail_run(
    conn: asyncpg.Connection,
    run_id: int,
    exc: Exception,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    await conn.execute(
        """
        UPDATE ingestion_runs
        SET status='failed', finished_at=NOW(), error_message=$2
        WHERE id=$1
        """,
        run_id,
        str(exc),
    )
    await conn.execute(
        """
        INSERT INTO ingestion_errors (ingestion_run_id, context, payload, message)
        VALUES ($1, $2, $3, $4)
        """,
        run_id,
        str(context),
        {},
        str(exc),
    )

