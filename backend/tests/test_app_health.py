import pytest

from app.db.deps import get_db_connection
from app.main import app


def test_health_endpoint_returns_ok(client) -> None:  # type: ignore[no-untyped-def]
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.fixture
def override_db_dependency():
    class DummyConnection:
        async def execute(self, query: str) -> None:  # noqa: ARG002
            return None

    async def _get_conn():
        dummy = DummyConnection()
        yield dummy

    app.dependency_overrides[get_db_connection] = _get_conn
    yield
    app.dependency_overrides.pop(get_db_connection, None)


def test_database_health_endpoint_checks_connection(client, override_db_dependency) -> None:  # type: ignore[no-untyped-def]
    response = client.get("/api/v1/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

