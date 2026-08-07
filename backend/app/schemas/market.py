from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class MarketInstrumentResponse(BaseModel):
    ticker: str
    provider_symbol: str
    exchange: str
    description: str = ""


class MarketInstrumentListResponse(BaseModel):
    source: str = "legacy_seed_registry"
    total_registry_size: int
    items: list[MarketInstrumentResponse]


class StockAnalysisRequest(BaseModel):
    language: Literal["ar", "en"] = "ar"


class StockAnalysisResponse(BaseModel):
    analysis_id: UUID
    ticker: str
    cached: bool
    market_snapshot_cached: bool
    charged_points: int = Field(ge=0)
    charged_coins: str
    balance_points: int = Field(ge=0)
    balance_coins: str
    data_as_of: datetime
    payload: dict


class StockComparisonRequest(BaseModel):
    request_key: str = Field(min_length=12, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    tickers: list[str] = Field(min_length=2, max_length=5)
    language: Literal["ar", "en"] = "ar"

    @field_validator("tickers")
    @classmethod
    def normalize_tickers(cls, value: list[str]) -> list[str]:
        normalized = [ticker.strip().upper() for ticker in value if ticker.strip()]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Choose different stock symbols")
        return normalized


class StockComparisonItemResponse(BaseModel):
    rank: int = Field(ge=1, le=5)
    ticker: str
    analysis_id: UUID
    data_as_of: datetime
    signal: str
    final_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=100)
    comparison_score: float = Field(ge=0, le=100)
    trend: str
    rsi: float
    average_volume_20: float = Field(ge=0)
    risk_level: str
    risk_score: float = Field(ge=0, le=100)
    entry: float = Field(ge=0)
    stop_loss: float = Field(ge=0)
    target_1: float = Field(ge=0)
    target_2: float = Field(ge=0)
    reward_risk_1: float = Field(ge=0)


class StockComparisonFailureResponse(BaseModel):
    ticker: str
    code: str
    message: str
    retryable: bool = True


class StockComparisonResponse(BaseModel):
    comparison_id: UUID
    request_key: str
    tickers: list[str]
    best_ticker: str
    summary: str
    items: list[StockComparisonItemResponse]
    failed_items: list[StockComparisonFailureResponse] = Field(default_factory=list)
    included_allowance: bool
    comparison_charged_points: int = Field(ge=0)
    comparison_charged_coins: str
    analysis_charged_points: int = Field(ge=0)
    analysis_charged_coins: str
    allowance_used: int = Field(ge=0)
    allowance_remaining: int = Field(ge=0)
    idempotent: bool
    balance_points: int = Field(ge=0)
    balance_coins: str
    disclaimer: str


class MarketQuoteResponse(BaseModel):
    ticker: str
    description: str = ""
    exchange: str = "EGX"
    sector: str | None = None
    current_price: float | None = None
    open_price: float | None = None
    previous_close: float | None = None
    session_high: float | None = None
    session_low: float | None = None
    change: float | None = None
    change_percent: float | None = None
    volume: float | None = None
    week52_high: float | None = None
    week52_low: float | None = None
    market_open: bool = False
    session_change_percent: float | None = None
    session_date: str | None = None
    next_session_open: datetime | None = None


class MarketQuotesResponse(BaseModel):
    source: str
    generated_at: datetime
    market_open: bool
    next_session_open: datetime | None = None
    items: list[MarketQuoteResponse]
