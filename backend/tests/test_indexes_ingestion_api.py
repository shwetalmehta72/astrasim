from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


async def fake_backfill(symbol, start, end):
    return 12


async def fake_update(symbol):
    return 3


def test_indexes_backfill_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.indexes_ingestion.backfill_index_series", fake_backfill)

    response = client.post(
        "/api/v1/ingestion/indexes/backfill",
        json={"symbol": "SPX", "start": "2015-01-01", "end": "2016-01-01"},
    )

    assert response.status_code == 202
    assert response.json() == {"status": "ok", "rows": 12}


def test_indexes_update_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.indexes_ingestion.update_index_series", fake_update)

    response = client.post("/api/v1/ingestion/indexes/update", json={"symbol": "VIX"})

    assert response.status_code == 202
    assert response.json() == {"status": "ok", "rows": 3}

