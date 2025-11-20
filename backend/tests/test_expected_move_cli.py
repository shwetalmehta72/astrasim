import asyncio
import sys

from app.cli import run_expected_move as cli


def test_expected_move_cli(monkeypatch):
    called = {}

    async def fake_compute(symbol, horizon, use_latest=False):
        called["symbol"] = symbol
        called["horizon"] = horizon
        called["use_latest"] = use_latest
        return {
            "symbol": symbol.upper(),
            "horizon": horizon or 30,
            "expected_move_abs": 5.0,
            "expected_move_pct": 0.03,
            "surface_expected_move": 4.8,
            "realized_expected_move": 4.5,
            "pct_diff_surface": 0.02,
            "pct_diff_realized": 0.05,
            "severity_surface": "OK",
            "severity_realized": "OK",
            "atm_implied_vol": 0.25,
        }

    def fake_run(coro):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(coro)
        loop.close()

    monkeypatch.setattr("app.cli.run_expected_move.compute_expected_move", fake_compute)
    monkeypatch.setattr(cli.asyncio, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["prog", "AAPL", "30"])

    cli.main()

    assert called["symbol"] == "AAPL"
    assert called["horizon"] == 30

