from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SectorPerformance(BaseModel):
    sector: str
    avg_change_pct: float


class MarketBreadthResponse(BaseModel):
    """اتساع السوق — صاعد/هابط/ثابت + أداء قطاعي."""

    advancers: int
    decliners: int
    unchanged: int
    total: int
    advance_decline_ratio: float
    sector_performance: list[SectorPerformance] = Field(default_factory=list)
    as_of: datetime
    available: bool = True
    source: str | None = None
    error: str | None = None
