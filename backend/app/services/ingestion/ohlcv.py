from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import asyncpg

from app.clients.polygon import PolygonClient
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.connection import get_pool

logger = get_logger("ingestion.ohlcv")


class IngestionError(Exception):
    """Raised when ingestion fails."""


async def backfill_ohlcv(symbol: str, start: date, end: date, *, settings: Optional[Settings] = None) -> int:
    settings = settings or get_settings()
    if start > end:
        raise ValueError("start must be before end")

    async with PolygonClient(settings=settings) as client:
        pool = await get_pool()
        async with pool.acquire() as conn:
            run_id = await _create_run(conn, source="polygon_ohlcv_backfill")
            try:
                security_id = await _lookup_security_id(conn, symbol)
                rows = await _ingest_range(conn, client, security_id, symbol.upper(), start, end)
                await _complete_run(conn, run_id, rows_inserted=rows)
                logger.info("Backfill completed for %s (%s rows)", symbol, rows)
                return rows
            except Exception as exc:
                await _fail_run(
                    conn,
                    run_id,
                    exc,
                    context={"symbol": symbol.upper(), "start": start.isoformat(), "end": end.isoformat()},
                )
                raise


async def update_ohlcv(symbol: str, *, settings: Optional[Settings] = None) -> int:
    settings = settings or get_settings()
    async with PolygonClient(settings=settings) as client:
        pool = await get_pool()
        async with pool.acquire() as conn:
            run_id = await _create_run(conn, source="polygon_ohlcv_update")
            try:
                security_id = await _lookup_security_id(conn, symbol)
                start_date = await _determine_update_start(conn, security_id)
                end_date = date.today()
                rows = await _ingest_range(conn, client, security_id, symbol.upper(), start_date, end_date)
                await _complete_run(conn, run_id, rows_inserted=rows)
                logger.info("Update completed for %s (%s rows)", symbol, rows)
                return rows
            except Exception as exc:
                await _fail_run(conn, run_id, exc, context={"symbol": symbol.upper()})
                raise


async def _determine_update_start(conn: asyncpg.Connection, security_id: int) -> date:
    latest: Optional[datetime] = await conn.fetchval(
        "SELECT MAX(time) FROM ohlcv_bars WHERE security_id=$1 AND interval='1d'",
        security_id,
    )
    if latest:
        candidate = latest.date() - timedelta(days=1)
        return max(candidate, date.today() - timedelta(days=30))
    return date.today() - timedelta(days=30)


async def _ingest_range(
    conn: asyncpg.Connection,
    client: PolygonClient,
    security_id: int,
    symbol: str,
    start: date,
    end: date,
) -> int:
    if start > end:
        return 0

    bars = await client.fetch_ohlcv_range(symbol, start, end)
    if not bars:
        return 0

    payload = [
        (
            bar["time"],
            security_id,
            bar["interval"],
            bar["open"],
            bar["high"],
            bar["low"],
            bar["close"],
            bar["volume"],
            bar["source"],
        )
        for bar in bars
    ]

    insert_sql = """
        INSERT INTO ohlcv_bars (
            time, security_id, interval, open, high, low, close, volume, source
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
        ON CONFLICT (security_id, time, interval)
        DO UPDATE SET open=EXCLUDED.open,
                      high=EXCLUDED.high,
                      low=EXCLUDED.low,
                      close=EXCLUDED.close,
                      volume=EXCLUDED.volume,
                      source=EXCLUDED.source
    """

    await conn.executemany(insert_sql, payload)
    return len(payload)


async def _lookup_security_id(conn: asyncpg.Connection, symbol: str) -> int:
    security_id: Optional[int] = await conn.fetchval(
        "SELECT id FROM securities WHERE symbol=$1 LIMIT 1",
        symbol.upper(),
    )
    if security_id is None:
        raise IngestionError(f"Security {symbol} not found")
    return security_id


async def _create_run(conn: asyncpg.Connection, *, source: str) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO ingestion_runs (source, target_table, status)
        VALUES ($1, 'ohlcv_bars', 'running')
        RETURNING id
        """,
        source,
    )
    return int(row["id"])


async def _complete_run(conn: asyncpg.Connection, run_id: int, *, rows_inserted: int) -> None:
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
