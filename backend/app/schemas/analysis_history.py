"""Schemas for the user's recent analyses endpoint."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnalysisHistoryItem(BaseModel):
    """ملخص تحليل سابق — بدون payload كامل لتوفير الباندويث."""

    model_config = ConfigDict(from_attributes=True)

    analysis_id: UUID
    ticker: str
    signal: str
    score: float
    confidence: float
    price_at_analysis: float | None = None
    data_as_of: datetime
    engine_version: str = "v2.4"
    cached: bool = False


class AnalysisHistoryResponse(BaseModel):
    items: list[AnalysisHistoryItem]
    count: int
