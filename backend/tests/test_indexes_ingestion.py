from datetime import date, datetime, timezone

import pytest

from app.services.ingestion import indexes
from app.services.ingestion.indexes import (
    IndexIngestionError,
    backfill_index_series,
    update_index_series,
)


class FakeClient:
    def __init__(self, series):
        self.series = series

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def fetch_series(self, symbol, start, end):
        return self.series


class FakeConnection:
    def __init__(self):
        self.executed = []
        self.executemany_payloads = []
        self.security_id = None
        self.latest_time = None

    async def fetchrow(self, query, *args):
        if "INSERT INTO securities" in query and self.security_id is None:
            self.security_id = 11
            return {"id": self.security_id}
        if "SELECT id FROM securities" in query:
            if self.security_id:
                return {"id": self.security_id}
            return None
        return {"id": 11}

    async def fetchval(self, query, *args):
        if "MAX(time)" in query:
            return self.latest_time
        return None

    async def executemany(self, sql, payload):
        self.executemany_payloads.append(payload)

    async def execute(self, sql, *args):
        self.executed.append((sql.strip(), args))


class FakePool:
    def __init__(self, conn):
        self.conn = conn

    def acquire(self):
        return self

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


def patch_dependencies(monkeypatch, conn, series):
    async def fake_get_pool():
        return FakePool(conn)

    monkeypatch.setattr(indexes, "get_pool", fake_get_pool)
    monkeypatch.setattr(indexes, "PolygonIndexesClient", lambda settings=None: FakeClient(series))


@pytest.mark.asyncio
async def test_backfill_inserts_series(monkeypatch):
    conn = FakeConnection()
    series = [
        {
            "symbol": "SPX",
            "time": datetime(2023, 1, 1, tzinfo=timezone.utc),
            "open": 1,
            "high": 2,
            "low": 0.5,
            "close": 1.5,
            "volume": 0,
            "source": "polygon",
        }
    ]
    patch_dependencies(monkeypatch, conn, series)

    rows = await backfill_index_series("SPX", date(2023, 1, 1), date(2023, 1, 2))

    assert rows == 1
    assert len(conn.executemany_payloads[0]) == 1
    assert any("status='success'" in sql for sql, _ in conn.executed)


@pytest.mark.asyncio
async def test_backfill_creates_security_if_missing(monkeypatch):
    conn = FakeConnection()
    conn.security_id = None
    series = []
    patch_dependencies(monkeypatch, conn, series)

    rows = await backfill_index_series("VIX", date(2023, 1, 1), date(2023, 1, 2))

    assert rows == 0
    assert conn.security_id == 11


@pytest.mark.asyncio
async def test_update_uses_recent_window(monkeypatch):
    conn = FakeConnection()
    conn.security_id = 5
    conn.latest_time = datetime(2023, 1, 10, tzinfo=timezone.utc)
    series = [
        {
            "symbol": "NDX",
            "time": datetime(2023, 1, 9, tzinfo=timezone.utc),
            "open": 2,
            "high": 3,
            "low": 1,
            "close": 2.5,
            "volume": 10,
            "source": "polygon",
        }
    ]
    patch_dependencies(monkeypatch, conn, series)

    rows = await update_index_series("NDX")

    assert rows == 1
    assert len(conn.executemany_payloads[0]) == 1

