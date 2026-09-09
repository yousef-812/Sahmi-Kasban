from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.market_data.provider import get_market_data_provider
from app.market_data.types import MarketDataProvider
from app.models import MarketDataSnapshot
from app.services.stock_report import (
    generate_stock_report,
    persist_stock_report_snapshot,
    stock_report_to_dict,
)

router = APIRouter(prefix="/admin/stock-report", tags=["admin-stock-report"])
AdminMarketProvider = Annotated[
    MarketDataProvider,
    Depends(get_market_data_provider),
]


@router.get("")
async def get_stock_report(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    provider: AdminMarketProvider,
):
    """Return the latest cached admin stock report, or generate a fresh one when none exists."""
    try:
        snapshot = db.scalar(
            select(MarketDataSnapshot)
            .where(MarketDataSnapshot.ticker == "__STOCK_REPORT__")
            .order_by(desc(MarketDataSnapshot.fetched_at))
            .limit(1)
        )
        if snapshot is not None and snapshot.payload:
            return {
                **snapshot.payload,
                "source": "cached",
                "generated_at": snapshot.fetched_at.isoformat(),
            }
        result = await generate_stock_report(db, provider=provider)
        return {
            **stock_report_to_dict(result),
            "source": "live",
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"فشل إنشاء تقرير الأسهم: {str(exc)}",
        ) from exc


@router.post("/refresh")
async def refresh_stock_report(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    provider: AdminMarketProvider,
):
    """Force-generate a fresh admin stock report and persist it as the cached snapshot."""
    try:
        result = await generate_stock_report(db, provider=provider)
        persist_stock_report_snapshot(db, result)
        return {
            **stock_report_to_dict(result),
            "source": "live",
        }
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"فشل إنشاء تقرير الأسهم: {str(exc)}",
        ) from exc
