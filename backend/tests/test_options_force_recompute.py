from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_force_recompute_atm(monkeypatch):
    flags = {}

    async def fake_ingest(symbol, target_date, *, force=False, **kwargs):
        flags["force"] = force
        return {"symbol": symbol, "straddle_mid": 5.0, "dte": 30}

    monkeypatch.setattr("app.api.v1.routes.atm_straddles.ingest_atm_straddle", fake_ingest)
    response = client.post("/api/v1/options/straddles/ingest?force=true", json={"symbol": "AAPL"})
    assert response.status_code == 202
    assert flags.get("force") is True


def test_force_recompute_surface(monkeypatch):
    flags = {}

    async def fake_compute(symbol, target_date=None, *, force=False, **kwargs):
        flags["force"] = force
        return {"symbol": symbol, "dte": [], "moneyness": [], "iv_grid": []}

    monkeypatch.setattr("app.api.v1.routes.vol_surface.compute_surface", fake_compute)
    response = client.post("/api/v1/options/surface/compute?force=true", json={"symbol": "AAPL"})
    assert response.status_code == 202
    assert flags.get("force") is True


def test_force_recompute_expected_move(monkeypatch):
    flags = {}

    async def fake_compute(symbol, horizon, *, use_latest=False, force=False):
        flags["force"] = force
        return {
            "id": 1,
            "symbol": symbol,
            "horizon": horizon or 30,
            "expected_move_abs": 5.0,
            "expected_move_pct": 0.03,
            "surface_expected_move": 4.8,
            "realized_expected_move": 4.5,
            "pct_diff_surface": 0.02,
            "pct_diff_realized": 0.05,
            "severity_surface": "OK",
            "severity_realized": "OK",
        }

    monkeypatch.setattr("app.api.v1.routes.expected_move.compute_expected_move", fake_compute)
    response = client.post("/api/v1/options/expected-move/compute?force=true", json={"symbol": "AAPL"})
    assert response.status_code == 202
    assert flags.get("force") is True

