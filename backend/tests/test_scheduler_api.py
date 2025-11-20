from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


async def fake_run_backfill(ingestion_type, symbols, start, end):
    return {"success": len(symbols), "failed": 0, "manifest_ids": list(range(len(symbols)))}


async def fake_run_job(job_id):
    return None


async def fake_start_scheduler():
    return True


def test_scheduler_backfill_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.scheduler.run_backfill", fake_run_backfill)

    response = client.post(
        "/api/v1/scheduler/backfill",
        json={"ingestion_type": "ohlcv", "symbols": ["AAPL", "MSFT"], "start": "2020-01-01", "end": "2020-01-10"},
    )

    assert response.status_code == 202
    assert response.json()["success"] == 2


def test_scheduler_run_job_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.scheduler.run_job_now", fake_run_job)

    response = client.post("/api/v1/scheduler/run/update_ohlcv")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_scheduler_status_endpoint(monkeypatch):
    monkeypatch.setattr("app.api.v1.routes.scheduler.start_scheduler", fake_start_scheduler)
    monkeypatch.setattr("app.api.v1.routes.scheduler.get_job_status", lambda: {"job": {"next_run_time": None}})

    response = client.get("/api/v1/scheduler/status")
    assert response.status_code == 200
    assert "job" in response.json()

