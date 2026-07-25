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
    app_public_url: str = "http://localhost:8000"

    database_url: str = "sqlite+pysqlite:///./sahmi_kasban_dev.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    access_token_minutes: int = 15
    refresh_token_days: int = 30
    email_verification_hours: int = 24
    password_reset_minutes: int = 30
    jwt_algorithm: str = "HS256"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@sahmi-kasban.local"
    smtp_use_tls: bool = True

    market_data_primary: str = "tradingview"
    market_data_fallback: str = "yfinance"
    market_timezone: str = "Africa/Cairo"
    market_data_period: str = "1y"
    market_data_interval: str = "1d"
    market_data_cache_minutes: int = 30
    market_data_timeout_seconds: float = 20.0
    market_data_min_candles: int = 200

    tradingview_websocket_url: str = (
        "wss://data.tradingview.com/socket.io/websocket"
    )
    tradingview_origin: str = "https://www.tradingview.com"
    tradingview_user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36"
    )
    tradingview_auth_token: str = "unauthorized_user_token"

    analysis_cost_points: int = 50
    analysis_default_capital: float = 150_000.0
    analysis_risk_per_trade: float = 0.01
    analysis_max_position_value: float = 40_000.0
    analysis_engine_version: str = "core-v1"

    @model_validator(mode="after")
    def validate_sensitive_settings(self) -> Settings:
        if self.app_env in {Environment.STAGING, Environment.PRODUCTION}:
            if len(self.secret_key.strip()) < 32:
                raise ValueError(
                    "SECRET_KEY must contain at least 32 characters outside development"
                )
            if not self.database_url.startswith("postgresql"):
                raise ValueError(
                    "PostgreSQL is required outside development and test environments"
                )
            if not self.smtp_host:
                raise ValueError(
                    "SMTP_HOST is required outside development and test environments"
                )
        if self.market_data_cache_minutes <= 0:
            raise ValueError("MARKET_DATA_CACHE_MINUTES must be positive")
        if self.market_data_timeout_seconds <= 0:
            raise ValueError("MARKET_DATA_TIMEOUT_SECONDS must be positive")
        if self.market_data_min_candles < 60:
            raise ValueError("MARKET_DATA_MIN_CANDLES must be at least 60")
        if not self.tradingview_websocket_url.startswith("wss://"):
            raise ValueError("TRADINGVIEW_WEBSOCKET_URL must use wss://")
        if not self.tradingview_origin.startswith("https://"):
            raise ValueError("TRADINGVIEW_ORIGIN must use https://")
        if not self.tradingview_auth_token.strip():
            raise ValueError("TRADINGVIEW_AUTH_TOKEN must not be empty")
        if self.analysis_cost_points <= 0:
            raise ValueError("ANALYSIS_COST_POINTS must be positive")
        if self.analysis_default_capital <= 0:
            raise ValueError("ANALYSIS_DEFAULT_CAPITAL must be positive")
        if not 0 < self.analysis_risk_per_trade <= 0.10:
            raise ValueError(
                "ANALYSIS_RISK_PER_TRADE must be between 0 and 0.10"
            )
        if self.analysis_max_position_value <= 0:
            raise ValueError("ANALYSIS_MAX_POSITION_VALUE must be positive")
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
