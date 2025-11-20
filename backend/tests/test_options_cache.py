from datetime import timedelta

from app.core.config import Settings
from app.services.options import cache


def test_chain_cache_hit():
    settings = Settings()
    cache.invalidate_all()
    data = [{"strike": 100}]
    cache.set_cached_chain("AAPL", "2025-01-17", data, {"source": "live"}, settings=settings)
    result = cache.get_cached_chain("AAPL", "2025-01-17", settings=settings)
    assert result is not None
    assert result.value == data
    cache.invalidate_all()


def test_chain_cache_expiry():
    settings = Settings(OPTIONS_CACHE_TTL_CHAIN=0)
    cache.invalidate_all()
    cache.set_cached_chain("AAPL", "2025-01-17", [{"strike": 101}], settings=settings)
    result = cache.get_cached_chain("AAPL", "2025-01-17", settings=settings)
    assert result is None
    cache.invalidate_all()


def test_atm_cache():
    settings = Settings()
    cache.invalidate_all()
    payload = {"straddle_mid": 5.0, "dte": 30}
    cache.set_cached_atm("AAPL", payload, {"underlying_price": 150}, settings=settings)
    result = cache.get_cached_atm("AAPL", settings=settings)
    assert result is not None
    assert result.value["straddle_mid"] == 5.0
    cache.invalidate_all()


def test_surface_cache():
    settings = Settings()
    cache.invalidate_all()
    payload = {"symbol": "AAPL", "dte": [30], "moneyness": [0.0], "iv_grid": [[0.3]]}
    cache.set_cached_surface("AAPL", payload, {"source": "live"}, settings=settings)
    result = cache.get_cached_surface("AAPL", settings=settings)
    assert result is not None
    assert result.value["symbol"] == "AAPL"
    cache.invalidate_all()

