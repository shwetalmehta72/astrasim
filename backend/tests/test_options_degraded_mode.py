from datetime import datetime, timezone

import pytest

from app.services.options import degraded_mode


class FakeConn:
    def __init__(self, snapshot_ts=None, rows=None):
        self.snapshot_ts = snapshot_ts
        self.rows = rows or []

    async def fetchval(self, query, *args):
        return self.snapshot_ts

    async def fetch(self, query, *args):
        return self.rows


@pytest.mark.asyncio
async def test_fallback_chain_from_snapshot():
    rows = [
        {
            "option_symbol": "OPT1",
            "strike": 150,
            "expiration": datetime(2025, 1, 17, tzinfo=timezone.utc).date(),
            "call_put": "call",
            "bid": 2.0,
            "ask": 2.5,
            "mid": 2.25,
            "volume": 100,
            "open_interest": 200,
            "underlying_price": 149.5,
            "raw_payload": {},
        }
    ]
    conn = FakeConn(snapshot_ts=datetime.now(timezone.utc), rows=rows)
    chain = await degraded_mode.fallback_chain_from_snapshot(conn, 1, rows[0]["expiration"])
    assert chain is not None
    assert chain[0]["option_symbol"] == "OPT1"

