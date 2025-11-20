from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import build_request_logger, configure_logging
from app.db.connection import close_db_connection, connect_to_db


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.APP_DEBUG,
    )

    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.middleware("http")(build_request_logger())
    register_exception_handlers(app)

    @app.on_event("startup")
    async def startup() -> None:
        await connect_to_db()

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await close_db_connection()

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["system"], deprecated=True)
    async def legacy_health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

