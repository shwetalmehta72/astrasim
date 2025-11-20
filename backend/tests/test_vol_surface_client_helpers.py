from datetime import date

from app.clients.polygon_options import PolygonOptionsClient


def test_calculate_moneyness():
    m = PolygonOptionsClient.calculate_moneyness(110, 100)
    assert round(m, 2) == 0.10


def test_nearest_option_by_moneyness_prefers_closest():
    chain = [
        {"strike": 105, "call_put": "call", "volume": 200, "open_interest": 0, "mid": 1.5},
        {"strike": 110, "call_put": "call", "volume": 50, "open_interest": 200, "mid": 2.0},
        {"strike": 120, "call_put": "call", "volume": 10, "open_interest": 5, "mid": 2.5},
    ]
    option = PolygonOptionsClient.nearest_option_by_moneyness(
        chain,
        target_strike=111,
        option_type="call",
        min_liquidity=100,
    )
    assert option["strike"] == 110

