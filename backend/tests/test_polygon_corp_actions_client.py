from datetime import date
from typing import List

import httpx
import pytest

from app.clients.polygon_corp_actions import PolygonCorpActionsClient
from app.core.config import Settings


def _dividend_payload(ts: int) -> dict:
    return {
        "ticker": "AAPL",
        "ex_dividend_date": "2023-01-01",
        "record_date": "2023-01-02",
        "payment_date": "2023-01-03",
        "cash_amount": 0.25,
        "timestamp": ts,
    }


def _split_payload(ratio: float, execution: str) -> dict:
    return {
        "ticker": "AAPL",
        "execution_date": execution,
        "record_date": execution,
        "payable_date": execution,
        "ratio": ratio,
    }


@pytest.mark.asyncio
async def test_fetch_dividends_paginates():
    settings = Settings(POLYGON_API_KEY="test")
    calls: List[str] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        if len(calls) == 1:
            return httpx.Response(
                200,
                json={"results": [_dividend_payload(1)], "next_url": f"{settings.POLYGON_BASE_URL}/next"},
            )
        return httpx.Response(200, json={"results": [_dividend_payload(2)]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url=settings.POLYGON_BASE_URL) as http_client:
        client = PolygonCorpActionsClient(settings=settings, http_client=http_client)
        dividends = await client.fetch_dividends("AAPL", date(2023, 1, 1), date(2023, 1, 10))
        await client.close()

    assert len(dividends) == 2
    assert "/v3/reference/dividends" in calls[0]


@pytest.mark.asyncio
async def test_fetch_splits_normalizes_ratio():
    settings = Settings(POLYGON_API_KEY="test")

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": [_split_payload(4.0, "2023-02-01")]})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, base_url=settings.POLYGON_BASE_URL) as http_client:
        client = PolygonCorpActionsClient(settings=settings, http_client=http_client)
        splits = await client.fetch_splits("MSFT", date(2023, 1, 1), date(2023, 3, 1))
        await client.close()

    assert splits[0]["split_ratio"] == 4.0
    assert splits[0]["action_type"] == "split"

