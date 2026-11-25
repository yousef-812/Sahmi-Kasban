from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class EarningsEventResponse(BaseModel):
    """موعد إعلان أرباح مسجّل من مصدر حقيقي."""

    ticker: str
    event_date: date
    period: str | None = None
    estimate_eps: float | None = None
    actual_eps: float | None = None
    source: str


class EarningsCalendarResponse(BaseModel):
    """تقويم الأرباح — ``available:false`` و``source:null`` عند غياب بيانات حقيقية."""

    ticker: str | None = None
    days: int
    available: bool
    source: str | None
    items: list[EarningsEventResponse] = Field(default_factory=list)
    as_of: datetime | None = None
