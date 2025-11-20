from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    APP_NAME: str = "AstraSim Backend"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = Field(default_factory=list)

    DB_HOST: str = Field(default="localhost", alias="DATABASE_HOST")
    DB_PORT: int = Field(default=5432, alias="DATABASE_PORT")
    DB_NAME: str = Field(default="astrasim", alias="DATABASE_NAME")
    DB_USER: str = Field(default="astrasim", alias="DATABASE_USER")
    DB_PASSWORD: str = Field(default="astrasim", alias="DATABASE_PASSWORD")

    POLYGON_API_KEY: str = Field(default="", alias="POLYGON_API_KEY")
    POLYGON_OPTIONS_API_KEY: str = Field(default="", alias="POLYGON_OPTIONS_API_KEY")
    POLYGON_BASE_URL: str = "https://api.polygon.io"
    INGESTION_MAX_ATTEMPTS: int = 5
    INGESTION_RATE_LIMIT_SLEEP: float = 1.0
    CORP_ACTIONS_PAGE_LIMIT: int = 1000
    INDEX_PAGE_LIMIT: int = 50000
    VALIDATION_DEFAULT_LOOKBACK_DAYS: int = 30
    VALIDATION_INDEX_ETF_THRESHOLD: float = 0.1
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "UTC"
    JOB_INTERVAL_MINUTES: int = 60
    OPTIONS_SCHEMA_VERSION: str = "v1"
    OPTIONS_DEFAULT_DTE_TARGET: int = 30
    OPTIONS_MIN_DTE_BUFFER: int = 7
    OPTIONS_MONEINESS_WINDOW: float = 0.05
    VOL_SURFACE_DTE_BUCKETS: list[int] = Field(
        default_factory=lambda: [7, 14, 21, 30, 45, 60]
    )
    VOL_SURFACE_MONEYNESS_GRID: list[float] = Field(
        default_factory=lambda: [-0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20]
    )
    VOL_SURFACE_MIN_LIQUIDITY: int = 100
    VOL_SURFACE_MIN_DTE: int = 5
    VOL_SURFACE_MAX_DTE: int = 60
    VOL_SURFACE_MAX_BUCKET_DRIFT: int = 5
    EXPECTED_MOVE_TOL_IV: float = 0.1
    EXPECTED_MOVE_TOL_REALIZED: float = 0.15
    EXPECTED_MOVE_WARN_THRESHOLD: float = 0.1
    EXPECTED_MOVE_SEVERE_THRESHOLD: float = 0.25

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if value is None:
            return []
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

