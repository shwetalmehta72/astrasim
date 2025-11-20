import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    async def fake_connect_to_db() -> None:
        return None

    async def fake_close_db_connection() -> None:
        return None

    monkeypatch.setattr("app.main.connect_to_db", fake_connect_to_db)
    monkeypatch.setattr("app.main.close_db_connection", fake_close_db_connection)

    with TestClient(app) as test_client:
        yield test_client

