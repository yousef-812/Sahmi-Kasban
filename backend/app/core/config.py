from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Sahmi Kasban API"
    app_env: Environment = Environment.DEVELOPMENT
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    secret_key: str = ""
    cors_origins: str = ""

    database_url: str = "sqlite+pysqlite:///./sahmi_kasban_dev.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    market_data_primary: str = "tradingview"
    market_data_fallback: str = "yfinance"
    market_timezone: str = "Africa/Cairo"

    @model_validator(mode="after")
    def validate_sensitive_settings(self) -> "Settings":
        if self.app_env in {Environment.STAGING, Environment.PRODUCTION}:
            if len(self.secret_key.strip()) < 32:
                raise ValueError("SECRET_KEY must contain at least 32 characters outside development")
            if not self.database_url.startswith("postgresql"):
                raise ValueError("PostgreSQL is required outside development and test environments")
        return self

    @property
    def cors_origin_list(self) -> tuple[str, ...]:
        return tuple(
            item.strip()
            for item in self.cors_origins.split(",")
            if item.strip()
        )

    @property
    def is_production(self) -> bool:
        return self.app_env is Environment.PRODUCTION


@lru_cache
def get_settings() -> Settings:
    return Settings()
