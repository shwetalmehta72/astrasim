from datetime import date, datetime, timezone

import pytest

from app.services.ingestion import ohlcv
from app.services.ingestion.ohlcv import IngestionError, backfill_ohlcv, update_ohlcv


class FakePolygonClient:
    def __init__(self, results):
        self._results = results

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def fetch_ohlcv_range(self, symbol, start, end):
        return self._results


class FakeConnection:
    def __init__(self):
        self.executed = []
        self.executemany_payloads = []
        self.security_exists = True
        self.latest_time = None

    async def fetchval(self, query, *args):
        if "FROM securities" in query:
            return 1 if self.security_exists else None
        if "MAX(time)" in query:
            return self.latest_time
        return None

    async def fetchrow(self, query, *args):
        return {"id": 10}

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


def patch_dependencies(monkeypatch, conn, polygon_results):
    async def fake_get_pool():
        return FakePool(conn)

    monkeypatch.setattr(ohlcv, "get_pool", fake_get_pool)
    monkeypatch.setattr(ohlcv, "PolygonClient", lambda settings=None: FakePolygonClient(polygon_results))


@pytest.mark.asyncio
async def test_backfill_writes_rows(monkeypatch):
    conn = FakeConnection()
    bars = [
        {
            "time": datetime(2023, 1, 1, tzinfo=timezone.utc),
            "interval": "1d",
            "open": 1,
            "high": 2,
            "low": 0.5,
            "close": 1.5,
            "volume": 100,
            "source": "polygon",
        },
        {
            "time": datetime(2023, 1, 2, tzinfo=timezone.utc),
            "interval": "1d",
            "open": 2,
            "high": 3,
            "low": 1,
            "close": 2.5,
            "volume": 200,
            "source": "polygon",
        },
    ]
    patch_dependencies(monkeypatch, conn, bars)

    rows = await backfill_ohlcv("AAPL", date(2023, 1, 1), date(2023, 1, 2))

    assert rows == 2
    assert len(conn.executemany_payloads[0]) == 2
    statuses = [call[0] for call in conn.executed]
    assert any("status='success'" in sql for sql in statuses)


@pytest.mark.asyncio
async def test_backfill_logs_failure_when_security_missing(monkeypatch):
    conn = FakeConnection()
    conn.security_exists = False
    patch_dependencies(monkeypatch, conn, [])

    with pytest.raises(IngestionError):
        await backfill_ohlcv("UNKNOWN", date(2023, 1, 1), date(2023, 1, 2))

    assert any("status='failed'" in sql for sql, _ in conn.executed)


@pytest.mark.asyncio
async def test_update_uses_latest_timestamp(monkeypatch):
    conn = FakeConnection()
    conn.latest_time = datetime(2023, 1, 10, tzinfo=timezone.utc)
    bars = [
        {
            "time": datetime(2023, 1, 9, tzinfo=timezone.utc),
            "interval": "1d",
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "volume": 1,
            "source": "polygon",
        }
    ]
    patch_dependencies(monkeypatch, conn, bars)

    rows = await update_ohlcv("MSFT")

    assert rows == 1
    assert len(conn.executemany_payloads[0]) == 1
    assert any("status='success'" in sql for sql, _ in conn.executed)

