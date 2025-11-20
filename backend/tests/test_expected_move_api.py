from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


async def fake_compute(symbol, horizon, use_latest=False, force=False):
    return {
        "id": 1,
        "symbol": symbol.upper(),
        "horizon": horizon or 30,
        "expected_move_abs": 5.0,
        "expected_move_pct": 0.033,
        "surface_expected_move": 4.8,
        "realized_expected_move": 4.5,
        "pct_diff_surface": 0.04,
        "pct_diff_realized": 0.1,
        "severity_surface": "OK",
        "severity_realized": "WARN",
        "atm_implied_vol": 0.25,
    }


async def fake_get_recent(symbol, limit):
    return [
        {
            "symbol": symbol.upper(),
            "horizon": 30,
            "expected_move_abs": 5.0,
            "expected_move_pct": 0.033,
            "surface_expected_move": 4.8,
            "realized_expected_move": 4.5,
            "pct_diff_surface": 0.04,
            "pct_diff_realized": 0.1,
            "severity_surface": "OK",
            "severity_realized": "WARN",
            "snapshot_timestamp": "2025-01-01T00:00:00Z",
        }
    ]


def test_expected_move_compute_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.expected_move.compute_expected_move", fake_compute)
    response = client.post("/api/v1/options/expected-move/compute", json={"symbol": "AAPL", "horizon": 30})
    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "ok"
    assert body["horizon"] == 30


def test_expected_move_get_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.expected_move.get_recent_expected_moves", fake_get_recent)
    response = client.get("/api/v1/options/expected-move/AAPL")
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"

