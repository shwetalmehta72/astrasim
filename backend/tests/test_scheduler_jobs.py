import pytest

from app.services.scheduler import jobs


@pytest.mark.asyncio
async def test_job_update_ohlcv_calls_ingestion(monkeypatch):
    called = []

    async def fake_update(symbol):
        called.append(symbol)

    monkeypatch.setattr(jobs, "update_ohlcv", fake_update)

    await jobs.job_update_ohlcv()

    assert called == ["AAPL", "MSFT", "GOOGL"]


@pytest.mark.asyncio
async def test_job_validation_sweep_runs_validation(monkeypatch):
    called = []

    async def fake_run_validation(symbol, start, end):
        called.append(symbol)

    monkeypatch.setattr(jobs, "run_validation", fake_run_validation)

    await jobs.job_validation_sweep()

    assert called == ["SPY"]

