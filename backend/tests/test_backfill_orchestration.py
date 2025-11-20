from datetime import date

import pytest

from app.services.scheduler import backfill


class FakeConnection:
    def __init__(self):
        self.manifest_rows = []
        self.updated = []
        self.next_id = 1

    async def fetchrow(self, query, *args):
        if "INSERT INTO backfill_manifest" in query:
            row = {"id": self.next_id}
            self.manifest_rows.append((row["id"], args))
            self.next_id += 1
            return row
        return {"id": 1}

    async def execute(self, sql, *args):
        self.updated.append((sql.strip(), args))


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
async def test_run_backfill_updates_manifest(monkeypatch):
    conn = FakeConnection()

    async def fake_get_pool():
        return FakePool(conn)

    async def fake_backfill(symbol, start, end):
        return 1

    monkeypatch.setattr(backfill, "get_pool", fake_get_pool)
    monkeypatch.setitem(backfill.INGESTION_MAP, "ohlcv", fake_backfill)

    summary = await backfill.run_backfill("ohlcv", ["AAPL", "MSFT"], date(2020, 1, 1), date(2020, 1, 5))

    assert summary["success"] == 2
    statuses = [args[1] for _, args in conn.updated]
    assert statuses == ["success", "success"]

