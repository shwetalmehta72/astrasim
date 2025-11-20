from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


async def fake_ingest(symbol, target_date):
    return {
        "symbol": symbol.upper(),
        "expiration": "2025-12-19",
        "strike": 150.0,
        "call_mid": 4.2,
        "put_mid": 3.7,
        "straddle_mid": 7.9,
        "implied_vol": 0.3,
        "dte": 30,
        "snapshot_timestamp": "2025-01-01T00:00:00Z",
    }


async def fake_recent(symbol, limit=10):
    return [
        {
            "symbol": symbol.upper(),
            "expiration": "2025-12-19",
            "strike": 150.0,
            "call_mid": 4.2,
            "put_mid": 3.7,
            "straddle_mid": 7.9,
            "implied_vol": 0.3,
            "dte": 30,
            "snapshot_timestamp": "2025-01-01T00:00:00Z",
        }
    ]


def test_post_ingest_endpoint(monkeypatch):
    monkeypatch.setattr(
        "app.api.v1.routes.atm_straddles.ingest_atm_straddle",
        fake_ingest,
    )
    response = client.post(
        "/api/v1/options/straddles/ingest",
        json={"symbol": "AAPL"},
    )
    assert response.status_code == 202
    assert response.json()["status"] == "ok"


def test_get_recent_straddles(monkeypatch):
    monkeypatch.setattr(
        "app.api.v1.routes.atm_straddles.get_recent_atm_straddles",
        fake_recent,
    )
    response = client.get("/api/v1/options/straddles/AAPL")
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"

