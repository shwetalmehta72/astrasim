import math
from datetime import date

import pytest

from app.services.options import expected_move


class FakeAcquire:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakePool:
    def __init__(self, conn):
        self.conn = conn

    def acquire(self):
        return FakeAcquire(self.conn)


@pytest.mark.asyncio
async def test_compute_expected_move(monkeypatch):
    fake_conn = object()
    inserted_flags = []

    async def fake_get_pool():
        return FakePool(fake_conn)

    async def fake_create_run(conn):
        return 1

    async def fake_complete_run(conn, run_id, rows):
        assert rows == 1

    async def fake_security_id(conn, symbol):
        return 42

    async def fake_fetch_straddle(conn, security_id, horizon, use_latest):
        return ({"id": 9, "straddle_mid": 6.0, "dte": horizon or 30}, horizon or 30)

    async def fake_underlying(conn, security_id, target_date):
        return 150.0

    async def fake_surface_iv(symbol, target_dte, moneyness=0.0):
        return 0.25

    async def fake_realized_map(conn, security_id):
        return {7: 0.2, 14: 0.22, 21: 0.24}

    async def fake_insert_check(
        conn,
        security_id,
        horizon,
        expected_move_abs,
        expected_move_pct,
        surface_move,
        realized_move,
        pct_surface,
        pct_real,
        severity_surface,
        severity_realized,
        run_id,
        raw_payload,
    ):
        assert math.isclose(expected_move_abs, 6.0)
        assert raw_payload["straddle"]["id"] == 9
        return 100

    async def fake_insert_flag(
        conn,
        security_id,
        horizon,
        flag_type,
        pct_diff,
        tolerance,
        severity,
        run_id,
    ):
        inserted_flags.append(flag_type)

    monkeypatch.setattr(expected_move, "get_pool", fake_get_pool)
    monkeypatch.setattr(expected_move, "_create_ingestion_run", fake_create_run)
    monkeypatch.setattr(expected_move, "_complete_run", fake_complete_run)
    monkeypatch.setattr(expected_move, "_get_security_id", fake_security_id)
    monkeypatch.setattr(expected_move, "_fetch_straddle", fake_fetch_straddle)
    monkeypatch.setattr(expected_move, "get_underlying_price", fake_underlying)
    monkeypatch.setattr(expected_move, "get_surface_iv", fake_surface_iv)
    monkeypatch.setattr(expected_move, "_compute_realized_vol_map", fake_realized_map)
    monkeypatch.setattr(expected_move, "_insert_expected_move_check", fake_insert_check)
    monkeypatch.setattr(expected_move, "_maybe_insert_flag", fake_insert_flag)

    result = await expected_move.compute_expected_move("AAPL", 30)

    assert result["symbol"] == "AAPL"
    assert result["horizon"] == 30
    assert "SURFACE_MISMATCH" in inserted_flags or "REALIZED_MISMATCH" in inserted_flags

