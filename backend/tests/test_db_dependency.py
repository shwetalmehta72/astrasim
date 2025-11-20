import pytest

from app.db import deps


class DummyConnection:
    pass


class DummyAcquireContext:
    def __init__(self, connection: DummyConnection) -> None:
        self.connection = connection
        self.entered = False

    async def __aenter__(self) -> DummyConnection:
        self.entered = True
        return self.connection

    async def __aexit__(self, exc_type, exc, tb) -> bool:  # noqa: ANN001, D401
        return False


class DummyPool:
    def __init__(self, acquire_context: DummyAcquireContext) -> None:
        self.acquire_context = acquire_context

    def acquire(self) -> DummyAcquireContext:
        return self.acquire_context


@pytest.mark.asyncio
async def test_get_db_connection_yields_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    connection = DummyConnection()
    acquire_context = DummyAcquireContext(connection)
    pool = DummyPool(acquire_context)

    async def fake_get_pool():
        return pool

    monkeypatch.setattr(deps, "get_pool", fake_get_pool)

    generator = deps.get_db_connection()
    yielded_connection = await generator.__anext__()

    assert yielded_connection is connection
    assert acquire_context.entered is True

    await generator.aclose()

