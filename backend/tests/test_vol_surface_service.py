from datetime import date, timedelta

import pytest

from app.core.config import Settings
from app.services.options import vol_surface


class FakeClient:
    def __init__(self, expiration):
        self.expiration = expiration

    async def fetch_expirations(self, symbol):
        return [self.expiration]

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
                "volume": 200,
                "open_interest": 100,
                "underlying_price": 149.0,
                "raw": {"leg": "call"},
            },
            {
                "option_symbol": "PUT140",
                "strike": 140.0,
                "expiration": expiration,
                "call_put": "put",
                "bid": 3.0,
                "ask": 3.4,
                "mid": 3.2,
                "volume": 220,
                "open_interest": 90,
                "underlying_price": 149.0,
                "raw": {"leg": "put"},
            },
        ]

    async def close(self):
        return None


class FakeConnection:
    def __init__(self):
        self.chain_rows = []
        self.surface_rows = []
        self.recon_rows = []

    async def fetchval(self, query, *args):
        if "FROM securities" in query:
            return 1
        if "FROM ohlcv_bars" in query:
            return 149.0
        return None

    async def fetchrow(self, query, *args):
        if "INSERT INTO ingestion_runs" in query:
            return {"id": 1}
        if "INSERT INTO vol_surface_points" in query:
            self.surface_rows.append(args)
            return {"id": 1}
        return {"id": 1}

    async def executemany(self, query, rows):
        if "option_chain_raw" in query:
            self.chain_rows.extend(rows)

    async def execute(self, query, *args):
        if "reconciliation_log" in query:
            self.recon_rows.append((query.strip(), args))
        return None

    async def fetch(self, query, *args):
        return []


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
async def test_compute_surface(monkeypatch):
    conn = FakeConnection()

    async def fake_get_pool():
        return FakePool(conn)

    monkeypatch.setattr(vol_surface, "get_pool", fake_get_pool)

    expiration = date.today() + timedelta(days=30)
    client = FakeClient(expiration)
    settings = Settings(
        POLYGON_API_KEY="x",
        POLYGON_OPTIONS_API_KEY="y",
    )

    result = await vol_surface.compute_surface("AAPL", date.today(), client=client, settings=settings)

    assert result["symbol"] == "AAPL"
    assert conn.chain_rows

