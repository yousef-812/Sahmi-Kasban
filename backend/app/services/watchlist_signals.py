"""Lightweight signal refresh for watchlist items.

Reuses the cached market-data and analysis layers to avoid redundant fetches.
Returns a minimal snapshot (signal, score, price, change_pct).
"""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.market_data.provider import get_market_data_provider
from app.market_data.quotes import fetch_single_quote
from app.services.stock_analysis import execute_stock_analysis, get_stock_ai_service

logger = logging.getLogger(__name__)


async def refresh_watchlist_signal(db: Session, user: Any, ticker: str) -> dict[str, Any]:
    """Return a lightweight snapshot for a single ticker.

    The snapshot contains:
      - signal: BUY | WATCH | AVOID
      - score: final_score (0-100)
      - price: latest close
      - change_pct: daily change percentage
    """
    quote = await fetch_single_quote(db, ticker)
    price = float(quote.current_price if quote and quote.current_price is not None else 0.0)
    change_pct = float(quote.change_percent if quote and quote.change_percent is not None else 0.0)

    provider = get_market_data_provider()
    ai_service = get_stock_ai_service()

    execution = await execute_stock_analysis(
        db,
        user=user,
        ticker=ticker,
        provider=provider,
        ai_service=ai_service,
    )
    analysis = execution.analysis.payload.get("analysis", {})
    signal = str(analysis.get("signal", "WATCH"))
    score = float(analysis.get("final_score") or 0.0)

    return {
        "signal": signal,
        "score": score,
        "price": price,
        "change_pct": change_pct,
    }
