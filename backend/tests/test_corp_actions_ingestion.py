from datetime import date

import pytest

from app.services.ingestion import corp_actions
from app.services.ingestion.corp_actions import (
    CorporateActionIngestionError,
    backfill_corp_actions,
    update_corp_actions,
)


class FakeClient:
    def __init__(self, dividends, splits):
        self.dividends = dividends
        self.splits = splits

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def fetch_dividends(self, symbol, start, end):
        return self.dividends

    async def fetch_splits(self, symbol, start, end):
        return self.splits


class FakeConnection:
    def __init__(self):
        self.executed = []
        self.executemany_payloads = []
        self.security_exists = True
        self.latest_ex_date = None

    async def fetchval(self, query, *args):
        if "FROM securities" in query:
            return 1 if self.security_exists else None
        if "MAX(ex_date)" in query:
            return self.latest_ex_date
        return None

    async def fetchrow(self, query, *args):
        return {"id": 99}

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


def patch_dependencies(monkeypatch, conn, dividends=None, splits=None):
    dividends = dividends or []
    splits = splits or []

    async def fake_get_pool():
        return FakePool(conn)

    monkeypatch.setattr(corp_actions, "get_pool", fake_get_pool)
    monkeypatch.setattr(corp_actions, "PolygonCorpActionsClient", lambda settings=None: FakeClient(dividends, splits))


@pytest.mark.asyncio
async def test_backfill_inserts_dividends(monkeypatch):
    conn = FakeConnection()
    dividends = [
        {
            "symbol": "AAPL",
            "action_type": "dividend",
            "ex_date": "2023-01-01",
            "record_date": "2023-01-02",
            "pay_date": "2023-01-03",
            "amount": 0.22,
            "split_ratio": None,
            "raw_payload": {"cash_amount": 0.22},
        }
    ]
    patch_dependencies(monkeypatch, conn, dividends=dividends)

    rows = await backfill_corp_actions("AAPL", date(2023, 1, 1), date(2023, 1, 10))

    assert rows == 1
    assert len(conn.executemany_payloads[0]) == 1
    assert any("status='success'" in sql for sql, _ in conn.executed)


@pytest.mark.asyncio
async def test_backfill_logs_failure(monkeypatch):
    conn = FakeConnection()
    conn.security_exists = False
    patch_dependencies(monkeypatch, conn)

    with pytest.raises(CorporateActionIngestionError):
        await backfill_corp_actions("UNKNOWN", date(2023, 1, 1), date(2023, 1, 10))

    assert any("status='failed'" in sql for sql, _ in conn.executed)


@pytest.mark.asyncio
async def test_update_uses_recent_window(monkeypatch):
    conn = FakeConnection()
    conn.latest_ex_date = date(2023, 2, 1)
    splits = [
        {
            "symbol": "MSFT",
            "action_type": "split",
            "ex_date": "2023-01-15",
            "record_date": "2023-01-15",
            "pay_date": "2023-01-20",
            "amount": None,
            "split_ratio": 4.0,
            "raw_payload": {"ratio": 4.0},
        }
    ]
    patch_dependencies(monkeypatch, conn, splits=splits)

    rows = await update_corp_actions("MSFT")

    assert rows == 1
    assert len(conn.executemany_payloads[0]) == 1

