from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger("polygon.indexes")


class PolygonIndexesClientError(Exception):
    pass


class PolygonIndexesClient:
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

    async def fetch_series(self, ticker: str, start: date, end: date) -> List[Dict[str, Any]]:
        url = f"/v2/aggs/ticker/{ticker.upper()}/range/1/day/{start.isoformat()}/{end.isoformat()}"
        params = {"adjusted": "true", "sort": "asc", "limit": self.settings.INDEX_PAGE_LIMIT}

        results: List[Dict[str, Any]] = []
        next_url: Optional[str] = None

        while True:
            data = await self._request(url if next_url is None else next_url, params if next_url is None else None)
            for item in data.get("results", []):
                results.append(self._normalize(ticker, item))
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
                    logger.warning("Polygon index ingestion rate limited; retrying")
                    raise httpx.HTTPStatusError("Rate limited", request=response.request, response=response)
                response.raise_for_status()
                return response.json()

        raise PolygonIndexesClientError("Failed to fetch index/macro series from Polygon")

    @staticmethod
    def _normalize(ticker: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        ts = datetime.fromtimestamp(payload["t"] / 1000, tz=timezone.utc)
        volume = payload.get("v") or payload.get("n") or 0
        return {
            "symbol": ticker.upper(),
            "time": ts,
            "open": payload["o"],
            "high": payload["h"],
            "low": payload["l"],
            "close": payload["c"],
            "volume": volume,
            "source": "polygon",
        }

    async def __aenter__(self) -> "PolygonIndexesClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        await self.close()

