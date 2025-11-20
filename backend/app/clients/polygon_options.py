from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger("options.client")


class PolygonOptionsClientError(Exception):
    """Base exception for Polygon options client."""


class PolygonOptionsRateLimitError(PolygonOptionsClientError):
    """Raised when Polygon returns 429."""


class PolygonOptionsClient:
    def __init__(
        self,
        *,
        settings: Optional[Settings] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._client = http_client or httpx.AsyncClient(
            base_url=self.settings.POLYGON_BASE_URL,
            headers={"Authorization": f"Bearer {self.settings.POLYGON_OPTIONS_API_KEY}"},
            timeout=30.0,
        )
        self._owns_client = http_client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def fetch_expirations(self, symbol: str) -> List[date]:
        params = {
            "underlying_ticker": symbol.upper(),
            "limit": 1000,
            "order": "asc",
        }
        url = "/v3/reference/options/contracts"
        expirations: set[date] = set()

        while True:
            data = await self._request(url, params)
            for item in data.get("results", []):
                exp_str = (
                    item.get("expiration_date")
                    or item.get("details", {}).get("expiration_date")
                )
                if exp_str:
                    expirations.add(date.fromisoformat(exp_str))
            next_url = data.get("next_url")
            if not next_url:
                break
            url = next_url
            params = None

        return sorted(expirations)

    async def fetch_chain(self, symbol: str, expiration: date) -> List[Dict[str, Any]]:
        params = {
            "underlying_ticker": symbol.upper(),
            "expiration_date": expiration.isoformat(),
            "limit": 1000,
            "order": "asc",
        }
        url = "/v3/snapshot/options/{symbol}".format(symbol=symbol.upper())
        data = await self._request(url, params)
        results = data.get("results", [])

        normalized: List[Dict[str, Any]] = []
        for option in results:
            details = option.get("details", {})
            contract_symbol = details.get("ticker") or option.get("ticker")
            strike = details.get("strike_price") or option.get("strike_price")
            exp_str = details.get("expiration_date") or option.get("expiration_date")
            contract_type = (
                details.get("contract_type")
                or option.get("contract_type")
                or ""
            ).lower()
            quote = option.get("quote") or {}
            day = option.get("day") or {}

            if not contract_symbol or strike is None or exp_str is None:
                continue

            bid = quote.get("bid_price")
            ask = quote.get("ask_price")
            mid = None
            if bid is not None and ask is not None:
                mid = (bid + ask) / 2

            normalized.append(
                {
                    "option_symbol": contract_symbol,
                    "strike": float(strike),
                    "expiration": date.fromisoformat(exp_str),
                    "call_put": contract_type,
                    "bid": bid,
                    "ask": ask,
                    "mid": mid,
                    "volume": day.get("volume"),
                    "open_interest": option.get("open_interest"),
                    "underlying_price": option.get("underlying_price")
                    or option.get("underlying_asset", {}).get("price"),
                    "raw": option,
                }
            )

        return normalized

    async def _request(
        self,
        url: str,
        params: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        async for attempt in AsyncRetrying(
            reraise=True,
            stop=stop_after_attempt(self.settings.INGESTION_MAX_ATTEMPTS),
            wait=wait_exponential(multiplier=self.settings.INGESTION_RATE_LIMIT_SLEEP, min=1, max=10),
            retry=retry_if_exception_type(
                (PolygonOptionsRateLimitError, httpx.HTTPError)
            ),
        ):
            with attempt:
                response = await self._client.get(url, params=params)
                if response.status_code == 429:
                    logger.warning("Polygon options rate limited; backing off")
                    raise PolygonOptionsRateLimitError("Rate limited by Polygon")
                response.raise_for_status()
                return response.json()

        raise PolygonOptionsClientError("Failed to fetch data from Polygon")

    async def __aenter__(self) -> "PolygonOptionsClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        await self.close()

