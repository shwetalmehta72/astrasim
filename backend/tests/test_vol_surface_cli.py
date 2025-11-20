import asyncio
import sys

from app.cli import run_vol_surface as cli


def test_vol_surface_cli(monkeypatch):
    called = {}

    async def fake_compute(symbol, target_date, *, force=False):
        called["symbol"] = symbol
        called["date"] = target_date
        called["force"] = force
        return {}

    def fake_run(coro):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(coro)
        loop.close()

    monkeypatch.setattr("app.cli.run_vol_surface.compute_surface", fake_compute)
    monkeypatch.setattr(cli.asyncio, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["prog", "AAPL", "--target-date", "2025-02-01"])

    cli.main()

    assert called["symbol"] == "AAPL"

