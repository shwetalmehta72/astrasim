from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import asyncpg

from app.clients.polygon_options import PolygonOptionsClient
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.connection import get_pool

logger = get_logger("options.surface")


async def compute_surface(
    symbol: str,
    target_date: Optional[date] = None,
    *,
    client: Optional[PolygonOptionsClient] = None,
    settings: Optional[Settings] = None,
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
            underlying_price = await _get_underlying_price(conn, security_id, target_date)
            if underlying_price is None:
                raise ValueError(f"No underlying price found for {symbol}")

            expirations = await client.fetch_expirations(symbol)
            expirations = [
                exp
                for exp in expirations
                if settings.VOL_SURFACE_MIN_DTE
                <= (exp - target_date).days
                <= settings.VOL_SURFACE_MAX_DTE
            ]

            bucket_expirations: Dict[int, date] = {}
            for bucket in settings.VOL_SURFACE_DTE_BUCKETS:
                matched = _match_expiration_for_bucket(
                    expirations,
                    target_date,
                    bucket,
                    settings.VOL_SURFACE_MAX_BUCKET_DRIFT,
                )
                if matched:
                    bucket_expirations[bucket] = matched
                else:
                    await _log_issue(
                        conn,
                        security_id,
                        "vol_surface_missing_bucket",
                        {"bucket": bucket},
                        run_id,
                    )

            moneyness_grid = settings.VOL_SURFACE_MONEYNESS_GRID
            iv_grid: List[List[Optional[float]]] = []
            used_buckets: List[int] = []

            for bucket in settings.VOL_SURFACE_DTE_BUCKETS:
                expiration = bucket_expirations.get(bucket)
                if not expiration:
                    continue

                chain = await client.fetch_chain(symbol, expiration)
                await _insert_option_chain(conn, security_id, chain)

                bucket_row = await _process_bucket(
                    conn,
                    security_id,
                    chain,
                    underlying_price,
                    expiration,
                    bucket,
                    moneyness_grid,
                    settings,
                    run_id,
                )
                iv_grid.append(bucket_row)
                used_buckets.append(bucket)

            snapshot_ts = datetime.now(tz=timezone.utc)
            surface = {
                "symbol": symbol.upper(),
                "generated_at": snapshot_ts,
                "dte": used_buckets,
                "moneyness": moneyness_grid,
                "iv_grid": iv_grid,
            }

            await _complete_run(conn, run_id, len(used_buckets) * len(moneyness_grid))
            return surface
        except Exception as exc:  # noqa: BLE001
            logger.exception("Vol surface computation failed for %s: %s", symbol, exc)
            await _fail_run(conn, run_id, exc, {"symbol": symbol.upper()})
            raise
        finally:
            if owns_client:
                await client.close()

async def get_recent_surfaces(symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        security_id = await _get_security_id(conn, symbol)
        rows = await conn.fetch(
            """
            SELECT DISTINCT snapshot_timestamp
            FROM vol_surface_points
            WHERE security_id=$1
            ORDER BY snapshot_timestamp DESC
            LIMIT $2
            """,
            security_id,
            limit,
        )
        surfaces: List[Dict[str, Any]] = []
        for row in rows:
            ts = row["snapshot_timestamp"]
            points = await conn.fetch(
                """
                SELECT dte, moneyness, implied_vol
                FROM vol_surface_points
                WHERE security_id=$1 AND snapshot_timestamp=$2
                ORDER BY dte ASC, moneyness ASC
                """,
                security_id,
                ts,
            )
            surface_dict: Dict[int, Dict[float, float]] = {}
            moneyness_values = sorted({float(p["moneyness"]) for p in points})
            dte_values = sorted({int(p["dte"]) for p in points})
            for p in points:
                surface_dict.setdefault(int(p["dte"]), {})
                surface_dict[int(p["dte"])][float(p["moneyness"])] = p["implied_vol"]
            iv_grid: List[List[Optional[float]]] = []
            for dte in dte_values:
                row_vals = [
                    surface_dict.get(dte, {}).get(m)
                    for m in moneyness_values
                ]
                iv_grid.append(row_vals)
            surfaces.append(
                {
                    "symbol": symbol.upper(),
                    "generated_at": ts,
                    "dte": dte_values,
                    "moneyness": moneyness_values,
                    "iv_grid": iv_grid,
                }
            )
        return surfaces


def _match_expiration_for_bucket(
    expirations: List[date],
    target_date: date,
    bucket: int,
    max_drift: int,
) -> Optional[date]:
    candidates = []
    for exp in expirations:
        dte = (exp - target_date).days
        if dte < 0:
            continue
        candidates.append((abs(dte - bucket), exp))
    if not candidates:
        return None
    drift, best = min(candidates, key=lambda x: x[0])
    if drift > max_drift:
        return None
    return best


async def _process_bucket(
    conn: asyncpg.Connection,
    security_id: int,
    chain: List[Dict[str, Any]],
    underlying_price: float,
    expiration: date,
    bucket_dte: int,
    moneyness_grid: List[float],
    settings: Settings,
    run_id: int,
) -> List[Optional[float]]:
    snapshot_ts = datetime.now(tz=timezone.utc)
    iv_row: List[Optional[float]] = []
    for m in moneyness_grid:
        option_type = "put" if m <= 0 else "call"
        target_strike = underlying_price * (1 + m)
        option = PolygonOptionsClient.nearest_option_by_moneyness(
            chain,
            target_strike,
            option_type,
            settings.VOL_SURFACE_MIN_LIQUIDITY,
        )
        if not option:
            await _log_issue(
                conn,
                security_id,
                "vol_surface_missing_strike",
                {"moneyness": m, "dte": bucket_dte},
                run_id,
            )
            iv_row.append(None)
            continue

        mid = PolygonOptionsClient.option_mid(option)
        if not mid or mid <= 0:
            await _log_issue(
                conn,
                security_id,
                "vol_surface_invalid_mid",
                {"moneyness": m, "dte": bucket_dte},
                run_id,
            )
            iv_row.append(None)
            continue

        iv = _calculate_iv_proxy(mid, underlying_price, bucket_dte)
        if iv is None:
            iv_row.append(None)
            continue

        iv_row.append(iv)
        await conn.execute(
            """
            INSERT INTO vol_surface_points (
                security_id,
                expiration,
                dte,
                moneyness,
                strike,
                implied_vol,
                snapshot_timestamp,
                ingestion_run_id,
                raw_payload
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
            """,
            security_id,
            expiration,
            bucket_dte,
            m,
            option["strike"],
            iv,
            snapshot_ts,
            run_id,
            json.dumps(option["raw"]),
        )

    return iv_row


def _calculate_iv_proxy(mid: float, underlying_price: float, dte: int) -> Optional[float]:
    if underlying_price <= 0 or dte <= 0:
        return None
    try:
        return mid / (underlying_price * math.sqrt(dte / 365))
    except ZeroDivisionError:
        return None


async def _get_security_id(conn: asyncpg.Connection, symbol: str) -> int:
    security_id = await conn.fetchval(
        "SELECT id FROM securities WHERE symbol=$1 LIMIT 1",
        symbol.upper(),
    )
    if security_id is None:
        raise ValueError(f"Security {symbol} not found in securities table")
    return int(security_id)


async def _get_underlying_price(
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


async def _create_ingestion_run(conn: asyncpg.Connection) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO ingestion_runs (source, target_table, status)
        VALUES ('options_vol_surface', 'vol_surface_points', 'running')
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
        json.dumps(context or {}),
        "{}",
        str(exc),
    )


async def _log_issue(
    conn: asyncpg.Connection,
    security_id: int,
    issue_type: str,
    details: Dict[str, Any],
    ingestion_run_id: int,
) -> None:
    await conn.execute(
        """
        INSERT INTO reconciliation_log (security_id, issue_type, severity, details, issue_timestamp, ingestion_run_id)
        VALUES ($1, $2, 'WARN', $3, NOW(), $4)
        """,
        security_id,
        issue_type,
        json.dumps(details),
        ingestion_run_id,
    )
