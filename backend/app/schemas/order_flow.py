from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class OrderBookLevelResponse(BaseModel):
    price: float = Field(gt=0)
    size: float = Field(ge=0)


class OrderBookResponse(BaseModel):
    """درجة دفتر الأوامر (bid/ask) — تُفرَغ القوائم عند عدم توفّر مصدر عمق حقيقي."""

    available: bool
    ticker: str
    as_of: datetime | None = None
    bids: list[OrderBookLevelResponse] = Field(default_factory=list)
    asks: list[OrderBookLevelResponse] = Field(default_factory=list)
    provider: str | None = None
    reason: str | None = None


class RecentTradeItemResponse(BaseModel):
    executed_at: datetime | None = None
    price: float = Field(gt=0)
    size: float = Field(ge=0)
    turnover_egp: float = Field(ge=0)
    side: str = "unknown"


class RecentTradesResponse(BaseModel):
    """آخر الصفقات المنفّذة (time & sales) — تُفرَغ عند عدم توفّر مصدر صفقات حقيقي."""

    available: bool
    ticker: str
    items: list[RecentTradeItemResponse] = Field(default_factory=list)
    provider: str | None = None
    reason: str | None = None


class MarketDepthResponse(BaseModel):
    """ملخّص عمق السوق المُجمَّع — يعتمد على نفس قواعد الإتاحة الصادقة للدفتر."""

    available: bool
    ticker: str
    as_of: datetime | None = None
    levels: int = Field(ge=1)
    bid_levels: list[OrderBookLevelResponse] = Field(default_factory=list)
    ask_levels: list[OrderBookLevelResponse] = Field(default_factory=list)
    total_bid_volume: float = Field(ge=0, default=0.0)
    total_ask_volume: float = Field(ge=0, default=0.0)
    spread: float | None = None
    mid_price: float | None = None
    provider: str | None = None
    reason: str | None = None


class TopOfBookResponse(BaseModel):
    """أفضل سعر شراء/بيع لحظي (bid/ask) من اشتراك WS — بدون أحجام ولا سلّم."""

    available: bool
    ticker: str
    bid: float | None = None
    ask: float | None = None
    mid_price: float | None = None
    spread: float | None = None
    spread_bp: float | None = None
    as_of: datetime | None = None
    source: str | None = None
    reason: str | None = None


class WhaleActivityItemResponse(BaseModel):
    """جلسة تداول ذات دوران استثنائي — إشارة بديلة (proxy) لا بيانات order-flow."""

    session_date: str | None = None
    close: float = Field(gt=0)
    volume: float = Field(ge=0)
    turnover_egp: float = Field(ge=0)
    turnover_ratio: float | None = None


class WhaleDetectionResponse(BaseModel):
    """كشف «الحيتان» من الدوران اليومي — بديل موثّق عن كشف صفقات ضخمة فردية."""

    available: bool
    ticker: str
    threshold: float | None = None
    items: list[WhaleActivityItemResponse] = Field(default_factory=list)
