"""User recent analyses endpoint — fast retrieval without re-running analysis engines."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.models import StockAnalysis, UserStockAnalysisAccess
from app.schemas.analysis_history import (
    AnalysisHistoryItem,
    AnalysisHistoryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis-history", tags=["analysis-history"])

MAX_LIMIT = 20


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@router.get("", response_model=AnalysisHistoryResponse)
async def list_recent_analyses(
    user: CurrentUser,
    db: DatabaseSession,
    limit: int = Query(default=10, ge=1, le=MAX_LIMIT),
) -> AnalysisHistoryResponse:
    """Return the user's N most recent stock analyses."""
    rows = db.execute(
        select(UserStockAnalysisAccess, StockAnalysis)
        .join(StockAnalysis, StockAnalysis.id == UserStockAnalysisAccess.analysis_id)
        .where(UserStockAnalysisAccess.user_id == user.id)
        .order_by(UserStockAnalysisAccess.last_viewed_at.desc())
        .limit(limit)
    ).all()

    items: list[AnalysisHistoryItem] = []
    for _access, analysis in rows:
        payload = analysis.payload if isinstance(analysis.payload, dict) else {}
        analysis_data = payload.get("analysis", {}) if isinstance(payload.get("analysis"), dict) else {}
        engines = analysis_data.get("engines", {}) if isinstance(analysis_data.get("engines"), dict) else {}
        tech_details = (
            engines.get("technical", {}).get("details", {})
            if isinstance(engines.get("technical"), dict)
            else {}
        )

        signal = str(analysis_data.get("signal", "WATCH"))
        score = _safe_float(analysis_data.get("final_score")) or 0.0
        confidence = _safe_float(analysis_data.get("confidence")) or 0.0
        price = _safe_float(tech_details.get("close")) or _safe_float(payload.get("price_at_analysis"))
        version = str(payload.get("version", "v2.4"))

        items.append(
            AnalysisHistoryItem(
                analysis_id=analysis.id,
                ticker=analysis.ticker,
                signal=signal,
                score=score,
                confidence=confidence,
                price_at_analysis=price,
                data_as_of=analysis.data_as_of,
                engine_version=version,
                cached=True,
            )
        )

    return AnalysisHistoryResponse(items=items, count=len(items))
