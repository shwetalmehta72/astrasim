from __future__ import annotations

from datetime import date, datetime
from typing import Dict, Iterable, List, Optional

import asyncpg

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.db.connection import get_pool
from app.services.ingestion import (
    backfill_corp_actions,
    backfill_index_series,
    backfill_ohlcv,
)

logger = get_logger("scheduler.backfill")

INGESTION_MAP = {
    "ohlcv": backfill_ohlcv,
    "corp_actions": backfill_corp_actions,
    "indexes": backfill_index_series,
}


async def run_backfill(
    ingestion_type: str,
    symbols: Iterable[str],
    start: date,
    end: date,
    *,
    settings: Optional[Settings] = None,
) -> Dict[str, int | List[int]]:
    settings = settings or get_settings()
    func = INGESTION_MAP.get(ingestion_type)
    if func is None:
        raise ValueError(f"Unsupported ingestion type {ingestion_type}")

    pool = await get_pool()
    successes = 0
    failures = 0
    manifest_ids: List[int] = []

    async with pool.acquire() as conn:
        for symbol in symbols:
            manifest_id = await _create_manifest(conn, ingestion_type, symbol, start, end)
            manifest_ids.append(manifest_id)
            try:
                await func(symbol, start, end)
                await _update_manifest(conn, manifest_id, "success")
                successes += 1
                logger.info("Backfill success %s %s", ingestion_type, symbol)
            except Exception as exc:  # noqa: BLE001
                await _update_manifest(conn, manifest_id, "failed")
                logger.exception("Backfill failed for %s %s: %s", ingestion_type, symbol, exc)
                failures += 1

    return {"success": successes, "failed": failures, "manifest_ids": manifest_ids}


async def _create_manifest(
    conn: asyncpg.Connection,
    ingestion_type: str,
    symbol: str,
    start: date,
    end: date,
) -> int:
    row = await conn.fetchrow(
        """
        INSERT INTO backfill_manifest (ingestion_type, symbol, start_date, end_date)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """,
        ingestion_type,
        symbol.upper(),
        start,
        end,
    )
    return int(row["id"])


async def _update_manifest(conn: asyncpg.Connection, manifest_id: int, status: str) -> None:
    await conn.execute(
        """
        UPDATE backfill_manifest
        SET status=$2, completed_at=NOW()
        WHERE id=$1
        """,
        manifest_id,
        status,
    )

