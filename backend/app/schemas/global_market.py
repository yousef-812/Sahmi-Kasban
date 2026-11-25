from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

GlobalMarketKind = Literal["index", "fx", "metal", "energy"]


class GlobalMarketItemResponse(BaseModel):
    """عنصر سوق عالمي (مؤشر/زوج عملة/سلعة) — قيمته من مزوّد واحد موثّق."""

    symbol: str
    name: str
    name_ar: str
    value: float = Field(gt=0)
    change_pct: float | None = None
    currency: str | None = None
    kind: GlobalMarketKind


class GlobalMarketResponse(BaseModel):
    """سياق السوق العالمي/الماكرو — يُفرَغ بصدق إلى ``available: false`` عند تعذّر المصدر."""

    available: bool
    source: str | None = None
    as_of: datetime | None = None
    indices: list[GlobalMarketItemResponse] = Field(default_factory=list)
    fx: list[GlobalMarketItemResponse] = Field(default_factory=list)
    commodities: list[GlobalMarketItemResponse] = Field(default_factory=list)
    error: str | None = None
