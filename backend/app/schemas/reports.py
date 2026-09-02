from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MarketReportPreviewResponse(BaseModel):
    report_id: UUID
    source_session_date: date
    target_session_date: date
    generated_at: datetime
    status: str
    item_count: int = Field(ge=0, le=10)
    unlocked: bool
    unlock_cost_points: int = Field(ge=0)
    unlock_cost_coins: str
    market_summary: dict


class MarketReportItemResponse(BaseModel):
    ticker: str
    rank: int = Field(ge=1)
    score: float = Field(ge=0, le=100)
    payload: dict


class MarketReportResponse(BaseModel):
    report_id: UUID
    source_session_date: date
    target_session_date: date
    generated_at: datetime
    market_summary: dict
    items: list[MarketReportItemResponse]
    extended_items: list[MarketReportItemResponse] = Field(default_factory=list)


class MarketReportUnlockResponse(BaseModel):
    charged_points: int = Field(ge=0)
    charged_coins: str
    balance_points: int = Field(ge=0)
    balance_coins: str
    report: MarketReportResponse


class MarketReportHistoryResponse(BaseModel):
    history_days_allowed: int = Field(ge=0)
    plan_code: str
    reports: list[MarketReportPreviewResponse]
