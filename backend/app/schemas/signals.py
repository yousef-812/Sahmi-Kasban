"""Pydantic schemas for the signals and alerts API."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SignalEventOut(BaseModel):
    """Single lifecycle audit event."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event: str
    price: Decimal | None = None
    note: str | None = None
    created_at: datetime


class SignalOut(BaseModel):
    """Single trade signal returned to the mobile terminal."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticker: str
    direction: str
    entry: Decimal
    stop: Decimal
    t1: Decimal
    t2: Decimal | None = None
    t3: Decimal | None = None
    state: str
    opened_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    pnl_pct: Decimal | None = None
    source: str
    ref_report_id: UUID | None = None
    user_id: UUID | None = None
    meta: dict = Field(default_factory=dict)


class SignalDetailOut(SignalOut):
    """Signal with its full transition history."""

    events: list[SignalEventOut] = Field(default_factory=list)


class SignalListResponse(BaseModel):
    """Filtered signal list."""

    items: list[SignalOut]
    count: int


class SignalCreateIn(BaseModel):
    """Payload to open a manual trade signal."""

    ticker: str = Field(..., min_length=1, max_length=24)
    direction: str = Field(..., min_length=3, max_length=8)
    entry: float = Field(..., gt=0)
    stop: float = Field(..., gt=0)
    t1: float = Field(..., gt=0)
    t2: float | None = Field(default=None, gt=0)
    t3: float | None = Field(default=None, gt=0)


class SignalAdvanceIn(BaseModel):
    """Candle snapshot used to evaluate a signal (admin/testing helper)."""

    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)


class AlertOut(BaseModel):
    """Single in-app alert."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    ref_id: UUID | None = None
    title: str
    body: str
    is_read: bool = False
    created_at: datetime


class AlertListResponse(BaseModel):
    """Alert inbox page."""

    items: list[AlertOut]
    count: int


class AlertBulkReadResponse(BaseModel):
    """Result of marking every unread alert as read."""

    updated: int
