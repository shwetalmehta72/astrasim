from datetime import date, datetime, timezone
from typing import List

import httpx
import pytest

from app.clients.polygon import PolygonClient
from app.core.config import Settings


def _mock_response(timestamp_ms: int) -> dict:
    return {"t": timestamp_ms, "o": 1.0, "h": 2.0, "l": 0.5, "c": 1.5, "v": 100}


@pytest.mark.asyncio
async def test_fetch_ohlcv_range_handles_pagination():
    settings = Settings(POLYGON_API_KEY="test")

    calls: List[str] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if len(calls) == 1:
            return httpx.Response(
                200,
                json={"results": [_mock_response(1700000000000)], "next_url": f"{settings.POLYGON_BASE_URL}/next"},
            )
        if len(calls) == 2:
            return httpx.Response(200, json={"results": [_mock_response(1700001000000)]})
        raise AssertionError("Unexpected call")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url=settings.POLYGON_BASE_URL) as http_client:
        client = PolygonClient(settings=settings, http_client=http_client)
        bars = await client.fetch_ohlcv_range("AAPL", date(2023, 1, 1), date(2023, 1, 3))
        await client.close()

    assert len(bars) == 2
    assert bars[0]["time"].tzinfo == timezone.utc
    assert "/range/1/day/2023-01-01/2023-01-03" in calls[0]


@pytest.mark.asyncio
async def test_fetch_ohlcv_range_retries_rate_limit():
    settings = Settings(POLYGON_API_KEY="test", INGESTION_MAX_ATTEMPTS=3)
    attempt = {"count": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        attempt["count"] += 1
        if attempt["count"] == 1:
            return httpx.Response(429, json={"error": "Too many requests"})
        return httpx.Response(200, json={"results": [_mock_response(1700002000000)]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url=settings.POLYGON_BASE_URL) as http_client:
        client = PolygonClient(settings=settings, http_client=http_client)
        bars = await client.fetch_ohlcv_range("MSFT", date(2023, 1, 1), date(2023, 1, 2))
        await client.close()

    assert len(bars) == 1
    assert attempt["count"] == 2
