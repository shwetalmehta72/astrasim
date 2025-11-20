from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


async def fake_compute(symbol, target_date, *, force=False):
    return {
        "symbol": symbol.upper(),
        "dte": [30],
        "moneyness": [-0.1, 0.0, 0.1],
        "iv_grid": [[0.2, 0.25, 0.3]],
        "generated_at": "2025-01-01T00:00:00Z",
    }


async def fake_recent(symbol, limit):
    return [
        {
            "symbol": symbol.upper(),
            "dte": [30],
            "moneyness": [-0.1, 0.0, 0.1],
            "iv_grid": [[0.2, 0.25, 0.3]],
            "generated_at": "2025-01-01T00:00:00Z",
        }
    ]


def test_post_compute_surface(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.vol_surface.compute_surface", fake_compute)
    response = client.post("/api/v1/options/surface/compute", json={"symbol": "AAPL"})
    assert response.status_code == 202
    assert response.json()["status"] == "ok"


def test_get_surface(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.vol_surface.get_recent_surfaces", fake_recent)
    response = client.get("/api/v1/options/surface/AAPL")
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"

