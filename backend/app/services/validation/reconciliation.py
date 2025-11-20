from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Sequence

import asyncpg

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.connection import get_pool
from app.services.validation import validators

logger = get_logger("validation")


async def run_validation(
    symbol: str,
    start: datetime,
    end: datetime,
    *,
    settings: Optional[Settings] = None,
) -> int:
    settings = settings or get_settings()
    pool = await get_pool()
    async with pool.acquire() as conn:
        security = await _get_security(conn, symbol)
        rows = await _fetch_prices(conn, security["id"], start, end)
        corp_actions = await _fetch_corp_actions(conn, security["id"], start, end)

        issues = []
        issues.extend(
            validators.validate_missing_timestamps(
                security["id"],
                rows,
                expected_interval=timedelta(days=1),
            )
        )
        issues.extend(validators.validate_non_monotonic(security["id"], rows))
        issues.extend(validators.validate_zero_negative_prices(security["id"], rows))
        issues.extend(validators.validate_corp_actions_consistency(security["id"], corp_actions))

        return await _insert_issues(conn, issues, ingestion_run_id=None)


async def run_reconciliation(
    symbols: Sequence[str],
    start: datetime,
    end: datetime,
    *,
    settings: Optional[Settings] = None,
) -> int:
    if len(symbols) < 2:
        raise ValueError("reconciliation requires at least two symbols")

    settings = settings or get_settings()
    pool = await get_pool()
    async with pool.acquire() as conn:
        securities = [await _get_security(conn, sym) for sym in symbols]
        issues = []

        base_rows = await _fetch_prices(conn, securities[0]["id"], start, end)
        for sec in securities[1:]:
            compare_rows = await _fetch_prices(conn, sec["id"], start, end)
            issues.extend(
                validators.validate_index_vs_etf(
                    securities[0]["id"],
                    base_rows,
                    compare_rows,
                    settings.VALIDATION_INDEX_ETF_THRESHOLD,
                )
            )

        return await _insert_issues(conn, issues, ingestion_run_id=None)


async def _insert_issues(
    conn: asyncpg.Connection,
    issues: Iterable[Dict[str, Any]],
    ingestion_run_id: Optional[int],
) -> int:
    count = 0
    for issue in issues:
        await conn.execute(
            """
            INSERT INTO reconciliation_log (security_id, issue_type, severity, details, issue_timestamp, ingestion_run_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            issue["security_id"],
            issue["issue_type"],
            issue["severity"],
            json.dumps(issue["details"]),
            issue["issue_timestamp"],
            ingestion_run_id,
        )
        count += 1
    return count


async def _get_security(conn: asyncpg.Connection, symbol: str) -> Dict[str, Any]:
    row = await conn.fetchrow("SELECT id FROM securities WHERE symbol=$1 LIMIT 1", symbol.upper())
    if not row:
        raise ValueError(f"Security {symbol} not found")
    return dict(row)


async def _fetch_prices(
    conn: asyncpg.Connection,
    security_id: int,
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    rows = await conn.fetch(
        """
        SELECT time, open, high, low, close, volume
        FROM ohlcv_bars
        WHERE security_id=$1 AND interval='1d' AND time BETWEEN $2 AND $3
        ORDER BY time ASC
        """,
        security_id,
        start,
        end,
    )
    return [dict(row) for row in rows]


async def _fetch_corp_actions(
    conn: asyncpg.Connection,
    security_id: int,
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    rows = await conn.fetch(
        """
        SELECT action_type, ex_date
        FROM corporate_actions
        WHERE security_id=$1 AND ex_date BETWEEN $2::date AND $3::date
        ORDER BY ex_date ASC
        """,
        security_id,
        start.date(),
        end.date(),
    )
    return [dict(row) for row in rows]

