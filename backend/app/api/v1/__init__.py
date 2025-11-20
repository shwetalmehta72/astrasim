from fastapi import APIRouter

from app.api.v1.routes import (
    atm_straddles,
    corp_actions_ingestion,
    health,
    ingestion,
    indexes_ingestion,
    meta,
    scheduler,
    validation,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(meta.router, prefix="/meta", tags=["meta"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(corp_actions_ingestion.router, tags=["corp-actions"])
api_router.include_router(indexes_ingestion.router, tags=["indexes"])
api_router.include_router(validation.router, tags=["validation"])
api_router.include_router(scheduler.router, tags=["scheduler"])
api_router.include_router(atm_straddles.router, tags=["options"])

