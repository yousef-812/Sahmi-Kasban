from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import DatabaseSession
from app.market_data.egx_symbols import UnknownTickerError, normalize_egx_ticker
from app.schemas.earnings import EarningsCalendarResponse
from app.services.earnings import get_earnings_calendar, refresh_earnings_calendar

router = APIRouter(tags=["market"])


@router.get("/market/earnings-calendar", response_model=EarningsCalendarResponse)
async def get_earnings_calendar_endpoint(
    db: DatabaseSession,
    ticker: str = Query(default="", max_length=24),
    days: int = Query(default=30, ge=1, le=365),
) -> EarningsCalendarResponse:
    """تقويم الأرباح القادمة — يقرأ من جدول `earnings_calendar` فقط.

    يعيد 200 بقائمة فارغة و``available:false``/``source:null`` عندما لا تتوفر
    بيانات حقيقية (لا يُخترع أي تاريخ). عند وجود نتائج مخزّنة يُحدَّث الجدول
    من نفس مزوّد سكانر TradingView المعتمد بحد أقصى مرة كل 12 ساعة.
    """
    normalized: str | None = None
    if ticker.strip():
        try:
            normalized = normalize_egx_ticker(ticker)
        except UnknownTickerError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="رمز السهم غير صالح.",
            ) from exc

    payload = get_earnings_calendar(db, ticker=normalized, days=days)
    if not payload["items"]:
        await refresh_earnings_calendar(db)
        payload = get_earnings_calendar(db, ticker=normalized, days=days)
    return EarningsCalendarResponse(**payload)
