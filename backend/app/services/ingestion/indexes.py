from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import asyncpg

from app.clients.polygon_indexes import PolygonIndexesClient
from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.connection import get_pool

logger = get_logger("ingestion.indexes")

DEFAULT_INDEX_SYMBOLS = [
    "SPX",
    "NDX",
    "VIX",
    "TNX",
    "SPY",
    "QQQ",
    "XLF",
    "XLK",
    "XLE",
    "XLV",
    "XLY",
    "XLP",
    "XLI",
    "XLU",
]


class IndexIngestionError(Exception):
    pass


async def backfill_index_series(symbol: str, start: date, end: date, *, settings: Optional[Settings] = None) -> int:
    if start > end:
        raise ValueError("start must be before end")

    settings = settings or get_settings()
    async with PolygonIndexesClient(settings=settings) as client:
        pool = await get_pool()
        async with pool.acquire() as conn:
            run_id = await _create_run(conn, "polygon_index_backfill")
            try:
                security_id = await _ensure_security(conn, symbol)
                rows = await _ingest_range(conn, client, security_id, symbol.upper(), start, end)
                await _complete_run(conn, run_id, rows)
                logger.info("Index backfill completed for %s (%s rows)", symbol, rows)
                return rows
            except Exception as exc:
                await _fail_run(
                    conn,
                    run_id,
                    exc,
                    context={"symbol": symbol.upper(), "start": start.isoformat(), "end": end.isoformat()},
                )
                raise


async def update_index_series(symbol: str, *, settings: Optional[Settings] = None) -> int:
    settings = settings or get_settings()
    async with PolygonIndexesClient(settings=settings) as client:
        pool = await get_pool()
        async with pool.acquire() as conn:
            run_id = await _create_run(conn, "polygon_index_update")
            try:
                security_id = await _ensure_security(conn, symbol)
                start_date = await _determine_update_start(conn, security_id)
                end_date = date.today()
                rows = await _ingest_range(conn, client, security_id, symbol.upper(), start_date, end_date)
                await _complete_run(conn, run_id, rows)
                logger.info("Index update completed for %s (%s rows)", symbol, rows)
                return rows
            except Exception as exc:
                await _fail_run(conn, run_id, exc, context={"symbol": symbol.upper()})
                raise


async def _ingest_range(
    conn: asyncpg.Connection,
    client: PolygonIndexesClient,
    security_id: int,
    symbol: str,
    start: date,
    end: date,
) -> int:
    series = await client.fetch_series(symbol, start, end)
    if not series:
        return 0

    payload = [
        (
            record["time"],
            security_id,
            "1d",
            record["open"],
            record["high"],
            record["low"],
            record["close"],
            record["volume"] or 0,
            record["source"],
        )
        for record in series
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


async def _ensure_security(conn: asyncpg.Connection, symbol: str) -> int:
    existing = await conn.fetchrow("SELECT id FROM securities WHERE symbol=$1 LIMIT 1", symbol.upper())
    if existing:
        return int(existing["id"])

    row = await conn.fetchrow(
        """
        INSERT INTO securities (symbol, type, is_active)
        VALUES ($1, 'index', true)
        RETURNING id
        """,
        symbol.upper(),
    )
    return int(row["id"])


async def _determine_update_start(conn: asyncpg.Connection, security_id: int) -> date:
    latest: Optional[datetime] = await conn.fetchval(
        "SELECT MAX(time) FROM ohlcv_bars WHERE security_id=$1 AND interval='1d'",
        security_id,
    )
    if latest:
        return max(latest.date() - timedelta(days=5), date.today() - timedelta(days=30))
    return date.today() - timedelta(days=365)


async def _create_run(conn: asyncpg.Connection, source: str) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO ingestion_runs (source, target_table, status)
        VALUES ($1, 'ohlcv_bars', 'running')
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
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
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

