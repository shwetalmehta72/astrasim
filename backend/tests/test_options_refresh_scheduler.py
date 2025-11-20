import pytest

from app.services.scheduler import jobs


@pytest.mark.asyncio
async def test_job_refresh_options_atm(monkeypatch):
    called = []

    async def fake_ingest(symbol, *args, **kwargs):
        called.append(symbol)

    monkeypatch.setattr(jobs, "ingest_atm_straddle", fake_ingest)
    await jobs.job_refresh_options_atm()
    assert "AAPL" in called


@pytest.mark.asyncio
async def test_job_refresh_options_surface(monkeypatch):
    called = []

    async def fake_compute(symbol, *args, **kwargs):
        called.append(symbol)

    monkeypatch.setattr(jobs, "compute_surface", fake_compute)
    await jobs.job_refresh_options_surface()
    assert "AAPL" in called

