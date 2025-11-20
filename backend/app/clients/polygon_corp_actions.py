from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger("polygon.corp_actions")


class PolygonCorpActionsClientError(Exception):
    pass


class PolygonCorpActionsClient:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._client = http_client or httpx.AsyncClient(
            base_url=self.settings.POLYGON_BASE_URL,
            headers={"Authorization": f"Bearer {self.settings.POLYGON_API_KEY}"},
            timeout=30.0,
        )
        self._owns_client = http_client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def fetch_dividends(self, symbol: str, start: date, end: date) -> List[Dict[str, Any]]:
        return await self._fetch_paginated(
            "/v3/reference/dividends",
            {
                "ticker": symbol.upper(),
                "limit": self.settings.CORP_ACTIONS_PAGE_LIMIT,
                "ex_dividend_date.gte": start.isoformat(),
                "ex_dividend_date.lte": end.isoformat(),
                "sort": "ex_dividend_date",
                "order": "asc",
            },
            action_type="dividend",
        )

    async def fetch_splits(self, symbol: str, start: date, end: date) -> List[Dict[str, Any]]:
        return await self._fetch_paginated(
            "/v3/reference/splits",
            {
                "ticker": symbol.upper(),
                "limit": self.settings.CORP_ACTIONS_PAGE_LIMIT,
                "execution_date.gte": start.isoformat(),
                "execution_date.lte": end.isoformat(),
                "sort": "execution_date",
                "order": "asc",
            },
            action_type="split",
        )

    async def _fetch_paginated(
        self,
        endpoint: str,
        params: Dict[str, Any],
        *,
        action_type: str,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        next_url: Optional[str] = None

        while True:
            data = await self._request(endpoint if next_url is None else next_url, params if next_url is None else None)
            raw_results = data.get("results", [])
            for payload in raw_results:
                results.append(self._normalize(action_type, payload))

            next_url = data.get("next_url")
            if not next_url:
                break

        return results

    async def _request(self, url: str, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        async for attempt in AsyncRetrying(
            reraise=True,
            stop=stop_after_attempt(self.settings.INGESTION_MAX_ATTEMPTS),
            wait=wait_exponential(multiplier=self.settings.INGESTION_RATE_LIMIT_SLEEP, min=1, max=10),
            retry=retry_if_exception_type(httpx.HTTPError),
        ):
            with attempt:
                response = await self._client.get(url, params=params)
                if response.status_code == 429:
                    logger.warning("Polygon corporate actions rate limited; backing off")
                    raise httpx.HTTPStatusError("Rate limited", request=response.request, response=response)
                response.raise_for_status()
                return response.json()

        raise PolygonCorpActionsClientError("Failed to fetch data from Polygon corporate actions endpoints")

    @staticmethod
    def _normalize(action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if action_type == "dividend":
            return {
                "symbol": payload.get("ticker", "").upper(),
                "action_type": "dividend",
                "ex_date": payload.get("ex_dividend_date"),
                "record_date": payload.get("record_date"),
                "pay_date": payload.get("payment_date"),
                "amount": payload.get("cash_amount"),
                "split_ratio": None,
                "raw_payload": payload,
            }

        return {
            "symbol": payload.get("ticker", "").upper(),
            "action_type": "split",
            "ex_date": payload.get("execution_date"),
            "record_date": payload.get("record_date"),
            "pay_date": payload.get("payable_date"),
            "amount": None,
            "split_ratio": payload.get("ratio"),
            "raw_payload": payload,
        }

    async def __aenter__(self) -> "PolygonCorpActionsClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        await self.close()

