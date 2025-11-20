from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


async def fake_backfill(symbol, start, end):
    return 7


async def fake_update(symbol):
    return 2


def test_corp_actions_backfill_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.corp_actions_ingestion.backfill_corp_actions", fake_backfill)

    response = client.post(
        "/api/v1/ingestion/corp-actions/backfill",
        json={"symbol": "AAPL", "start": "2020-01-01", "end": "2020-12-31"},
    )

    assert response.status_code == 202
    assert response.json() == {"status": "ok", "rows": 7}


def test_corp_actions_update_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.corp_actions_ingestion.update_corp_actions", fake_update)

    response = client.post("/api/v1/ingestion/corp-actions/update", json={"symbol": "MSFT"})

    assert response.status_code == 202
    assert response.json() == {"status": "ok", "rows": 2}

