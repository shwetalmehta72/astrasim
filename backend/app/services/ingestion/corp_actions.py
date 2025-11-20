from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import asyncpg

from app.clients.polygon_corp_actions import PolygonCorpActionsClient
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.connection import get_pool

logger = get_logger("ingestion.corp_actions")


class CorporateActionIngestionError(Exception):
    pass


async def backfill_corp_actions(symbol: str, start: date, end: date, *, settings: Optional[Settings] = None) -> int:
    if start > end:
        raise ValueError("start must be before end")

    settings = settings or get_settings()
    async with PolygonCorpActionsClient(settings=settings) as client:
        pool = await get_pool()
        async with pool.acquire() as conn:
            run_id = await _create_run(conn, "polygon_corp_actions_backfill")
            try:
                security_id = await _lookup_security_id(conn, symbol)
                rows = await _ingest_range(conn, client, security_id, symbol.upper(), start, end)
                await _complete_run(conn, run_id, rows)
                logger.info("Corporate actions backfill complete for %s (%s rows)", symbol, rows)
                return rows
            except Exception as exc:
                await _fail_run(
                    conn,
                    run_id,
                    exc,
                    context={"symbol": symbol.upper(), "start": start.isoformat(), "end": end.isoformat()},
                )
                raise


async def update_corp_actions(symbol: str, *, settings: Optional[Settings] = None) -> int:
    settings = settings or get_settings()
    async with PolygonCorpActionsClient(settings=settings) as client:
        pool = await get_pool()
        async with pool.acquire() as conn:
            run_id = await _create_run(conn, "polygon_corp_actions_update")
            try:
                security_id = await _lookup_security_id(conn, symbol)
                start_date = await _determine_update_start(conn, security_id)
                end_date = date.today()
                rows = await _ingest_range(conn, client, security_id, symbol.upper(), start_date, end_date)
                await _complete_run(conn, run_id, rows)
                logger.info("Corporate actions update complete for %s (%s rows)", symbol, rows)
                return rows
            except Exception as exc:
                await _fail_run(conn, run_id, exc, context={"symbol": symbol.upper()})
                raise


async def _ingest_range(
    conn: asyncpg.Connection,
    client: PolygonCorpActionsClient,
    security_id: int,
    symbol: str,
    start: date,
    end: date,
) -> int:
    dividends = await client.fetch_dividends(symbol, start, end)
    splits = await client.fetch_splits(symbol, start, end)

    records = dividends + splits
    if not records:
        return 0

    payload = [
        (
            security_id,
            record["action_type"],
            _parse_date(record["ex_date"]),
            _parse_date(record["record_date"]),
            _parse_date(record["pay_date"]),
            record["amount"],
            record["split_ratio"],
            json.dumps(record["raw_payload"]),
        )
        for record in records
    ]

    insert_sql = """
        INSERT INTO corporate_actions (
            security_id, action_type, ex_date, record_date, pay_date, amount, split_ratio, raw_payload
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
        ON CONFLICT DO NOTHING
    """

    await conn.executemany(insert_sql, payload)
    return len(payload)


async def _determine_update_start(conn: asyncpg.Connection, security_id: int) -> date:
    latest: Optional[date] = await conn.fetchval(
        "SELECT MAX(ex_date) FROM corporate_actions WHERE security_id=$1",
        security_id,
    )
    if latest:
        candidate = latest - timedelta(days=7)
        return max(candidate, date.today() - timedelta(days=90))
    return date.today() - timedelta(days=365)


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value)


async def _lookup_security_id(conn: asyncpg.Connection, symbol: str) -> int:
    security_id = await conn.fetchval("SELECT id FROM securities WHERE symbol=$1 LIMIT 1", symbol.upper())
    if security_id is None:
        raise CorporateActionIngestionError(f"Security {symbol} not found")
    return int(security_id)


async def _create_run(conn: asyncpg.Connection, source: str) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO ingestion_runs (source, target_table, status)
        VALUES ($1, 'corporate_actions', 'running')
        RETURNING id
        """,
        source,
    )
    return int(row["id"])


async def _complete_run(conn: asyncpg.Connection, run_id: int, rows: int) -> None:
    await conn.execute(
        """
        UPDATE ingestion_runs
        SET status='success', finished_at=NOW(), rows_inserted=$2
        WHERE id=$1
        """,
        run_id,
        rows,
    )


async def _fail_run(
    conn: asyncpg.Connection,
    run_id: int,
    exc: Exception,
    *,
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
    context_str = None
    if context:
        context_str = ", ".join(f"{key}={value}" for key, value in context.items())
    await conn.execute(
        """
        INSERT INTO ingestion_errors (ingestion_run_id, context, payload, message)
        VALUES ($1, $2, $3, $4)
        """,
        run_id,
        context_str,
        json.dumps(context or {}),
        str(exc),
    )

