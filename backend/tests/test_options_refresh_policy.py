from datetime import datetime, timedelta, timezone

from app.core.config import Settings
from app.services.options import refresh_policy


def test_should_refresh_atm_with_interval(monkeypatch):
    settings = Settings(ATM_REFRESH_INTERVAL=60, MIN_UNDERLYING_MOVE=0.01)
    refresh_policy.record_atm_refresh("AAPL", 150.0)

    def fake_now():
        return datetime.now(timezone.utc) + timedelta(seconds=30)

    monkeypatch.setattr(refresh_policy, "_now", fake_now)
    assert not refresh_policy.should_refresh_atm("AAPL", 150.0, settings=settings)

    def fake_now_late():
        return datetime.now(timezone.utc) + timedelta(seconds=120)

    monkeypatch.setattr(refresh_policy, "_now", fake_now_late)
    assert refresh_policy.should_refresh_atm("AAPL", 150.0, settings=settings)


def test_should_refresh_chain_force():
    settings = Settings(OPTIONS_CACHE_TTL_CHAIN=999)
    refresh_policy.record_chain_refresh("AAPL", "2025-01-17")
    assert refresh_policy.should_refresh_chain("AAPL", "2025-01-17", settings=settings, force=True)

