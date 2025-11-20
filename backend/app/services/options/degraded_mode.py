from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncpg

from app.core.logging import get_logger

logger = get_logger("options.degraded")


async def fallback_chain_from_snapshot(
    conn: asyncpg.Connection,
    security_id: int,
    expiration: datetime.date,
) -> Optional[List[Dict[str, Any]]]:
    snapshot_ts = await conn.fetchval(
        """
        SELECT snapshot_timestamp
        FROM option_chain_raw
        WHERE security_id=$1 AND expiration=$2
        ORDER BY snapshot_timestamp DESC
        LIMIT 1
        """,
        security_id,
        expiration,
    )
    if snapshot_ts is None:
        return None
    rows = await conn.fetch(
        """
        SELECT option_symbol,
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
        FROM option_chain_raw
        WHERE security_id=$1 AND expiration=$2 AND snapshot_timestamp=$3
        """,
        security_id,
        expiration,
        snapshot_ts,
    )
    return [dict(row) for row in rows]


async def fallback_surface_from_snapshot(
    conn: asyncpg.Connection,
    security_id: int,
) -> Optional[Dict[str, Any]]:
    snapshot_ts = await conn.fetchval(
        """
        SELECT snapshot_timestamp
        FROM vol_surface_points
        WHERE security_id=$1
        ORDER BY snapshot_timestamp DESC
        LIMIT 1
        """,
        security_id,
    )
    if snapshot_ts is None:
        return None
    rows = await conn.fetch(
        """
        SELECT dte, moneyness, implied_vol
        FROM vol_surface_points
        WHERE security_id=$1 AND snapshot_timestamp=$2
        ORDER BY dte ASC, moneyness ASC
        """,
        security_id,
        snapshot_ts,
    )
    return {
        "snapshot_timestamp": snapshot_ts,
        "points": [dict(row) for row in rows],
    }


def build_degraded_metadata(source: str) -> Dict[str, Any]:
    return {
        "degraded": source != "live",
        "fallback_source": source,
    }

