from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class MarketInstrumentResponse(BaseModel):
    ticker: str
    provider_symbol: str
    exchange: str


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