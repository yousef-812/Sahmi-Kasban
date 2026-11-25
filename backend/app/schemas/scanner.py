"""Pydantic schemas for the scanner API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScannerItemOut(BaseModel):
    """One scanner snapshot: envelope fields plus the payload of its kind.

    The payload keys follow the egxbot parity shape (``technicalScore``,
    ``levels``, ``patterns``, ...) and are carried through as extra fields.
    """

    model_config = ConfigDict(from_attributes=True, extra="allow")

    kind: str
    symbol: str
    timeframe: str
    as_of: datetime
    score: float | None = None
    rating: str | None = None
    sector: str | None = None


class ScannerListResponse(BaseModel):
    """Newest snapshot per symbol for a single scanner kind."""

    items: list[ScannerItemOut]
    count: int


class ScannerSmcResponse(BaseModel):
    """Flattened result of the smart-money-concepts engine for one symbol."""

    symbol: str
    score: float
    details: dict
    reasons: list[str]
