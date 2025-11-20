from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter()


@router.get("/info")
async def meta_info(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION,
    }

