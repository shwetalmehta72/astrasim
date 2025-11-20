from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


async def fake_backfill(symbol, start, end):
    return 42


async def fake_update(symbol):
    return 5


def test_backfill_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.ingestion.backfill_ohlcv", fake_backfill)

    response = client.post(
        "/api/v1/ingestion/ohlcv/backfill",
        json={"symbol": "AAPL", "start": "2023-01-01", "end": "2023-01-05"},
    )

    assert response.status_code == 202
    assert response.json() == {"status": "ok", "rows": 42}


def test_update_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.ingestion.update_ohlcv", fake_update)

    response = client.post("/api/v1/ingestion/ohlcv/update", json={"symbol": "MSFT"})

    assert response.status_code == 202
    assert response.json() == {"status": "ok", "rows": 5}

