from __future__ import annotations

import logging
import time
from typing import Awaitable, Callable

from fastapi import Request, Response

from app.core.config import Settings

LOGGER_NAME = "astrasim"


def configure_logging(settings: Settings) -> None:
    level = logging.DEBUG if settings.APP_DEBUG else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str | None = None) -> logging.Logger:
    full_name = LOGGER_NAME if not name else f"{LOGGER_NAME}.{name}"
    return logging.getLogger(full_name)


RequestHandler = Callable[[Request], Awaitable[Response]]


def build_request_logger() -> Callable[[Request, RequestHandler], Awaitable[Response]]:
    logger = logging.getLogger(f"{LOGGER_NAME}.http")

    async def log_request(request: Request, call_next: RequestHandler) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    return log_request

