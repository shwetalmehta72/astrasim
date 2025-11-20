from datetime import date

import pytest

from app.clients.polygon_options import PolygonOptionsClient
from app.core.config import Settings


@pytest.mark.asyncio
async def test_polygon_options_client_fetch_chain(monkeypatch):
    settings = Settings(
        POLYGON_API_KEY="test",
        POLYGON_OPTIONS_API_KEY="test",
    )
    client = PolygonOptionsClient(settings=settings)

    async def fake_request(url, params):
        return {
            "results": [
                {
                    "details": {
                        "ticker": "OPT1",
                        "strike_price": 150,
                        "expiration_date": "2025-12-19",
                        "contract_type": "call",
                    },
                    "quote": {"bid_price": 4.0, "ask_price": 5.0},
                    "day": {"volume": 1000},
                    "open_interest": 500,
                    "underlying_price": 149.5,
                },
                {
                    "details": {
                        "ticker": "OPT2",
                        "strike_price": 150,
                        "expiration_date": "2025-12-19",
                        "contract_type": "put",
                    },
                    "quote": {"bid_price": 3.0, "ask_price": 3.5},
                    "day": {"volume": 900},
                    "open_interest": 450,
                    "underlying_price": 149.5,
                },
            ]
        }

    monkeypatch.setattr(client, "_request", fake_request)

    chain = await client.fetch_chain("AAPL", date(2025, 12, 19))
    await client.close()
    assert len(chain) == 2
    assert chain[0]["option_symbol"] == "OPT1"
    assert chain[0]["mid"] == pytest.approx(4.5)

