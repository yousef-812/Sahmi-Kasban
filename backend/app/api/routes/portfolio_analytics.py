"""Portfolio analytics endpoints — correlation, diversification, sector exposure."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.portfolio_analytics import PortfolioAnalyticsResponse
from app.services.portfolio_analytics import compute_portfolio_analytics

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/analytics", response_model=PortfolioAnalyticsResponse)
async def portfolio_analytics(
    db: DatabaseSession,
    user: CurrentUser,
) -> PortfolioAnalyticsResponse:
    """Correlation, diversification and sector exposure of the caller's open signals.

    Scoped to the authenticated user only. Computed live on every request; the
    underlying candles are served through the shared market-data snapshot cache
    (``market_data_cache_minutes`` TTL), so no additional response cache exists.
    """
    payload = await compute_portfolio_analytics(db, user.id)
    return PortfolioAnalyticsResponse(**payload)
