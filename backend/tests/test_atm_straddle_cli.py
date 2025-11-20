import asyncio
import sys

from app.cli import run_atm_straddle_ingestion as cli


def test_cli_invokes_service(monkeypatch):
    called = {}

    async def fake_ingest(symbol, target_date):
        called["symbol"] = symbol
        called["target_date"] = target_date
        return {}

    def fake_run(coro):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

    monkeypatch.setattr("app.cli.run_atm_straddle_ingestion.ingest_atm_straddle", fake_ingest)
    monkeypatch.setattr(cli.asyncio, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["prog", "AAPL", "--target-date", "2025-01-01"])

    cli.main()

    assert called["symbol"] == "AAPL"

