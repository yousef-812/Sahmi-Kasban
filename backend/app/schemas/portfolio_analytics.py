"""Pydantic schemas for the portfolio analytics API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PortfolioPositionOut(BaseModel):
    """One open-signal position inside the computed portfolio."""

    ticker: str
    direction: str
    entry: float
    stop: float
    current_price: float | None = None
    weight: float = Field(ge=0.0, le=1.0)
    sector: str | None = None
    unrealized_pct: float | None = None


class PortfolioCorrelationOut(BaseModel):
    """Pairwise Pearson correlation matrix over aligned daily close returns."""

    lookback_sessions: int = Field(ge=0)
    min_observations: int = Field(ge=0)
    tickers: list[str]
    matrix: dict[str, dict[str, float | None]]


class PortfolioDiversificationOut(BaseModel):
    """Concentration metrics computed from position weights."""

    herfindahl: float = Field(ge=0.0)
    effective_positions: float = Field(ge=0.0)
    concentration_flag: bool
    concentration_threshold: float


class PortfolioWatchlistOut(BaseModel):
    """Watchlist tickers used as an exposure hint and last-price fallback."""

    count: int = Field(ge=0)
    tickers: list[str]


class PortfolioAnalyticsResponse(BaseModel):
    """Full payload returned by GET /portfolio/analytics."""

    as_of: datetime
    position_count: int = Field(ge=0)
    positions: list[PortfolioPositionOut]
    correlation: PortfolioCorrelationOut
    diversification: PortfolioDiversificationOut
    sector_exposure: dict[str, float]
    watchlist: PortfolioWatchlistOut
    warnings: list[str]
    analytics_version: str
