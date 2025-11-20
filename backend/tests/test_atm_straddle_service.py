from datetime import date, timedelta

import pytest

from app.core.config import Settings
from app.services.options import atm_straddle


class FakeClient:
    async def fetch_expirations(self, symbol):
        return [date.today() + timedelta(days=10)]

    async def fetch_chain(self, symbol, expiration):
        return [
            {
                "option_symbol": "CALL150",
                "strike": 150.0,
                "expiration": expiration,
                "call_put": "call",
                "bid": 4.0,
                "ask": 4.4,
                "mid": 4.2,
                "volume": 100,
                "open_interest": 50,
                "underlying_price": 149.0,
                "raw": {"leg": "call"},
            },
            {
                "option_symbol": "PUT150",
                "strike": 150.0,
                "expiration": expiration,
                "call_put": "put",
                "bid": 3.5,
                "ask": 3.9,
                "mid": 3.7,
                "volume": 90,
                "open_interest": 40,
                "underlying_price": 149.0,
                "raw": {"leg": "put"},
            },
        ]

    async def close(self):
        return None


class FakeConnection:
    def __init__(self):
        self.inserted_chain = []
        self.straddle_row = None
        self.run_ids = []

    async def fetchval(self, query, *args):
        if "FROM securities" in query:
            return 1
        if "FROM ohlcv_bars" in query:
            return 149.0
        return None

    async def fetchrow(self, query, *args):
        if "INSERT INTO ingestion_runs" in query:
            run_id = len(self.run_ids) + 1
            self.run_ids.append(run_id)
            return {"id": run_id}
        if "INSERT INTO option_straddles" in query:
            self.straddle_row = args
            return {"id": 99}
        return {"id": 1}

    async def executemany(self, query, rows):
        self.inserted_chain.extend(rows)

    async def execute(self, query, *args):
        return None


class FakePool:
    def __init__(self, conn):
        self.conn = conn

    def acquire(self):
        return self

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_ingest_atm_straddle(monkeypatch):
    conn = FakeConnection()

    async def fake_get_pool():
        return FakePool(conn)

    monkeypatch.setattr(atm_straddle, "get_pool", fake_get_pool)

    settings = Settings(
        POLYGON_API_KEY="x",
        POLYGON_OPTIONS_API_KEY="y",
    )
    client = FakeClient()

    result = await atm_straddle.ingest_atm_straddle(
        "AAPL",
        date.today(),
        client=client,
        settings=settings,
    )

    assert result["straddle_mid"] == pytest.approx(7.9)
    assert len(conn.inserted_chain) == 2

