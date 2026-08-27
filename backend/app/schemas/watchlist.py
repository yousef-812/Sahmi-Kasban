"""Pydantic schemas for the watchlist API."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WatchlistItemOut(BaseModel):
    """Single watchlist entry returned to the mobile terminal."""

    model_config = ConfigDict(from_attributes=True)

    ticker: str
    added_at: datetime = Field(default_factory=datetime.now)
    last_signal: str | None = None
    last_score: float | None = None
    last_price: float | None = None
    last_change_pct: float | None = None
    last_checked_at: datetime | None = None
    notes: dict = Field(default_factory=dict)


class WatchlistAddIn(BaseModel):
    """Payload to add a ticker to the watchlist."""

    ticker: str = Field(..., min_length=1, max_length=24)
    notes: dict = Field(default_factory=dict)


class WatchlistBulkAddIn(BaseModel):
    """Add multiple tickers in one call."""

    tickers: list[str] = Field(..., min_length=1, max_length=20)


class WatchlistResponse(BaseModel):
    """Full watchlist response with metadata."""

    items: list[WatchlistItemOut]
    count: int
    max_items: int = 50
