from __future__ import annotations

import json
import math
import statistics
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import asyncpg

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.connection import get_pool
from app.services.options import cache
from app.services.options.atm_straddle import calculate_iv_proxy, get_underlying_price
from app.services.options.vol_surface import get_surface_iv

logger = get_logger("options.expected_move")


async def compute_expected_move(
    symbol: str,
    horizon: Optional[int] = None,
    *,
    use_latest: bool = False,
    force: bool = False,
    settings: Optional[Settings] = None,
) -> Dict[str, Any]:
    settings = settings or get_settings()
    pool = await get_pool()
    async with pool.acquire() as conn:
        run_id = await _create_ingestion_run(conn)
        try:
            security_id = await _get_security_id(conn, symbol)
            cached_atm = cache.get_cached_atm(symbol) if not force else None
            straddle_row: Optional[Dict[str, Any]] = None
            resolved_horizon: Optional[int] = None

            if cached_atm:
                cached_value = cached_atm.value
                cached_dte = cached_value.get("dte")
                if use_latest or horizon is None or cached_dte == horizon:
                    straddle_row = {
                        "id": cached_value.get("id"),
                        "straddle_mid": cached_value["straddle_mid"],
                        "dte": cached_dte,
                        "snapshot_timestamp": cached_value.get("snapshot_timestamp"),
                    }
                    resolved_horizon = cached_dte

            if straddle_row is None:
                straddle_row, resolved_horizon = await _fetch_straddle(
                    conn,
                    security_id,
                    horizon,
                    use_latest,
                )

            if resolved_horizon is None:
                raise ValueError("Unable to determine horizon for expected move")

            today = date.today()
            underlying_price = await get_underlying_price(conn, security_id, today)
            if underlying_price is None or underlying_price <= 0:
                raise ValueError("Missing underlying price for expected move")

            straddle_mid = float(straddle_row["straddle_mid"])
            expected_move_abs = straddle_mid
            expected_move_pct = (
                expected_move_abs / underlying_price if underlying_price else None
            )
            atm_iv = calculate_iv_proxy(straddle_mid, underlying_price, resolved_horizon)

            surface_iv = None
            cached_surface = cache.get_cached_surface(symbol) if not force else None
            if cached_surface:
                surface_iv = _surface_iv_from_cache(cached_surface.value, resolved_horizon)
            if surface_iv is None:
                surface_iv = await get_surface_iv(symbol, resolved_horizon, 0.0)
            surface_expected_move = None
            if surface_iv:
                surface_expected_move = (
                    underlying_price * surface_iv * math.sqrt(resolved_horizon / 365)
                )

            realized_map = await _compute_realized_vol_map(conn, security_id)
            realized_vol = _select_realized_vol(resolved_horizon, realized_map)
            realized_expected_move = None
            if realized_vol:
                realized_expected_move = (
                    underlying_price * realized_vol * math.sqrt(resolved_horizon / 252)
                )

            pct_diff_surface = _compute_pct_diff(
                expected_move_abs, surface_expected_move
            )
            pct_diff_realized = _compute_pct_diff(
                expected_move_abs, realized_expected_move
            )

            severity_surface = _classify_severity(pct_diff_surface, settings)
            severity_realized = _classify_severity(pct_diff_realized, settings)

            check_id = await _insert_expected_move_check(
                conn,
                security_id,
                resolved_horizon,
                expected_move_abs,
                expected_move_pct,
                surface_expected_move,
                realized_expected_move,
                pct_diff_surface,
                pct_diff_realized,
                severity_surface,
                severity_realized,
                run_id,
                {
                    "straddle": straddle_row,
                    "atm_iv": atm_iv,
                    "metadata": cached_atm.metadata if cached_atm else {},
                },
            )

            await _maybe_insert_flag(
                conn,
                security_id,
                resolved_horizon,
                "SURFACE_MISMATCH",
                pct_diff_surface,
                settings.EXPECTED_MOVE_TOL_IV,
                severity_surface,
                run_id,
            )
            await _maybe_insert_flag(
                conn,
                security_id,
                resolved_horizon,
                "REALIZED_MISMATCH",
                pct_diff_realized,
                settings.EXPECTED_MOVE_TOL_REALIZED,
                severity_realized,
                run_id,
            )

            await _complete_run(conn, run_id, 1)
            return {
                "id": check_id,
                "symbol": symbol.upper(),
                "horizon": resolved_horizon,
                "expected_move_abs": expected_move_abs,
                "expected_move_pct": expected_move_pct,
                "surface_expected_move": surface_expected_move,
                "realized_expected_move": realized_expected_move,
                "pct_diff_surface": pct_diff_surface,
                "pct_diff_realized": pct_diff_realized,
                "severity_surface": severity_surface,
                "severity_realized": severity_realized,
                "atm_implied_vol": atm_iv,
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("Expected move computation failed for %s: %s", symbol, exc)
            await _fail_run(conn, run_id, exc, {"symbol": symbol.upper()})
            raise


async def get_recent_expected_moves(symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        security_id = await _get_security_id(conn, symbol)
        rows = await conn.fetch(
            """
            SELECT horizon_days,
                   expected_move_abs,
                   expected_move_pct,
                   surface_expected_move,
                   realized_expected_move,
                   pct_diff_surface,
                   pct_diff_realized,
                   severity_surface,
                   severity_realized,
                   snapshot_timestamp
            FROM expected_move_checks
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
                "horizon": row["horizon_days"],
                "expected_move_abs": row["expected_move_abs"],
                "expected_move_pct": row["expected_move_pct"],
                "surface_expected_move": row["surface_expected_move"],
                "realized_expected_move": row["realized_expected_move"],
                "pct_diff_surface": row["pct_diff_surface"],
                "pct_diff_realized": row["pct_diff_realized"],
                "severity_surface": row["severity_surface"],
                "severity_realized": row["severity_realized"],
                "snapshot_timestamp": row["snapshot_timestamp"],
            }
            for row in rows
        ]


async def _fetch_straddle(
    conn: asyncpg.Connection,
    security_id: int,
    horizon: Optional[int],
    use_latest: bool,
) -> Tuple[Dict[str, Any], Optional[int]]:
    if use_latest or horizon is None:
        row = await conn.fetchrow(
            """
            SELECT id, straddle_mid, dte, snapshot_timestamp
            FROM option_straddles
            WHERE security_id=$1
            ORDER BY snapshot_timestamp DESC
            LIMIT 1
            """,
            security_id,
        )
        if not row:
            raise ValueError("No ATM straddles available for symbol")
        return dict(row), int(row["dte"])

    row = await conn.fetchrow(
        """
        SELECT id, straddle_mid, dte, snapshot_timestamp
        FROM option_straddles
        WHERE security_id=$1
        ORDER BY ABS(dte-$2), snapshot_timestamp DESC
        LIMIT 1
        """,
        security_id,
        horizon,
    )
    if not row:
        raise ValueError("No ATM straddles available for requested horizon")
    return dict(row), int(row["dte"])


async def _compute_realized_vol_map(
    conn: asyncpg.Connection,
    security_id: int,
) -> Dict[int, Optional[float]]:
    lookbacks = [7, 14, 21]
    rows = await conn.fetch(
        """
        SELECT close
        FROM ohlcv_bars
        WHERE security_id=$1 AND interval='1d'
        ORDER BY time DESC
        LIMIT 90
        """,
        security_id,
    )
    prices = [float(row["close"]) for row in rows][::-1]
    vol_map: Dict[int, Optional[float]] = {}
    for window in lookbacks:
        if len(prices) < window + 1:
            vol_map[window] = None
            continue
        window_prices = prices[-(window + 1):]
        returns = [
            math.log(window_prices[i + 1] / window_prices[i])
            for i in range(len(window_prices) - 1)
            if window_prices[i] > 0
        ]
        if len(returns) < 2:
            vol_map[window] = None
            continue
        vol_map[window] = statistics.stdev(returns) * math.sqrt(252)
    return vol_map


def _select_realized_vol(horizon: int, vol_map: Dict[int, Optional[float]]) -> Optional[float]:
    if horizon <= 7:
        return vol_map.get(7)
    if horizon <= 14:
        return vol_map.get(14)
    return vol_map.get(21)


def _compute_pct_diff(base: Optional[float], comparison: Optional[float]) -> Optional[float]:
    if base is None or comparison is None:
        return None
    if comparison == 0:
        return None
    return abs(base - comparison) / abs(comparison)


def _classify_severity(value: Optional[float], settings: Settings) -> Optional[str]:
    if value is None:
        return None
    if value < settings.EXPECTED_MOVE_WARN_THRESHOLD:
        return "OK"
    if value < settings.EXPECTED_MOVE_SEVERE_THRESHOLD:
        return "WARN"
    return "SEVERE"


async def _insert_expected_move_check(
    conn: asyncpg.Connection,
    security_id: int,
    horizon: int,
    expected_move_abs: float,
    expected_move_pct: Optional[float],
    surface_move: Optional[float],
    realized_move: Optional[float],
    pct_surface: Optional[float],
    pct_real: Optional[float],
    severity_surface: Optional[str],
    severity_realized: Optional[str],
    run_id: int,
    raw_payload: Dict[str, Any],
) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO expected_move_checks (
            security_id,
            horizon_days,
            expected_move_abs,
            expected_move_pct,
            surface_expected_move,
            realized_expected_move,
            pct_diff_surface,
            pct_diff_realized,
            severity_surface,
            severity_realized,
            ingestion_run_id,
            raw_payload
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
        RETURNING id
        """,
        security_id,
        horizon,
        expected_move_abs,
        expected_move_pct,
        surface_move,
        realized_move,
        pct_surface,
        pct_real,
        severity_surface,
        severity_realized,
        run_id,
        raw_payload,
    )
    return int(row["id"])


async def _maybe_insert_flag(
    conn: asyncpg.Connection,
    security_id: int,
    horizon: int,
    flag_type: str,
    pct_diff: Optional[float],
    tolerance: float,
    severity: Optional[str],
    run_id: int,
) -> None:
    if pct_diff is None or pct_diff <= tolerance or severity is None:
        return
    await conn.execute(
        """
        INSERT INTO calibration_flags (
            security_id,
            horizon_days,
            flag_type,
            severity,
            details,
            ingestion_run_id
        )
        VALUES ($1,$2,$3,$4,$5,$6)
        """,
        security_id,
        horizon,
        flag_type,
        severity,
        {"pct_diff": pct_diff},
        run_id,
    )


async def _create_ingestion_run(conn: asyncpg.Connection) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO ingestion_runs (source, target_table, status)
        VALUES ('options_expected_move', 'expected_move_checks', 'running')
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
        {},
        str(exc),
    )


async def _get_security_id(conn: asyncpg.Connection, symbol: str) -> int:
    security_id = await conn.fetchval(
        "SELECT id FROM securities WHERE symbol=$1 LIMIT 1",
        symbol.upper(),
    )
    if security_id is None:
        raise ValueError(f"Security {symbol} not found in securities table")
    return int(security_id)


def _surface_iv_from_cache(surface: Dict[str, Any], target_dte: int) -> Optional[float]:
    dtes = surface.get("dte")
    moneyness = surface.get("moneyness")
    grid = surface.get("iv_grid")
    if not dtes or not moneyness or not grid:
        return None
    m_index = min(range(len(moneyness)), key=lambda idx: abs(float(moneyness[idx]) - 0.0))
    closest_idx = min(range(len(dtes)), key=lambda idx: abs(dtes[idx] - target_dte))
    row = grid[closest_idx]
    if row is None or len(row) <= m_index:
        return None
    value = row[m_index]
    return value

