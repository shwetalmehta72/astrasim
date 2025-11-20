from datetime import date

import httpx
import pytest

from app.clients.polygon_indexes import PolygonIndexesClient
from app.core.config import Settings


@pytest.mark.asyncio
async def test_fetch_series_handles_pagination():
    settings = Settings(POLYGON_API_KEY="test")
    calls = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if len(calls) == 1:
            return httpx.Response(
                200,
                json={"results": [{"t": 1700000000000, "o": 1, "h": 2, "l": 0.5, "c": 1.5, "v": 100}], "next_url": "next"},
            )
        return httpx.Response(
            200,
            json={"results": [{"t": 1700001000000, "o": 2, "h": 3, "l": 1, "c": 2.5, "v": None}]},
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url=settings.POLYGON_BASE_URL) as http_client:
        client = PolygonIndexesClient(settings=settings, http_client=http_client)
        bars = await client.fetch_series("SPX", date(2023, 1, 1), date(2023, 1, 5))
        await client.close()

    assert len(bars) == 2
    assert bars[1]["volume"] == 0

