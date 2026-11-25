"""Market breadth (advancers/decliners + sector performance) — WP-33.

Computed from the daily quotes snapshot (fetch_market_quotes), no new
data sources. Honest `available:false` when the snapshot is missing.
"""

from __future__ import annotations

import logging
from statistics import mean

from sqlalchemy.orm import Session

from app.market_data.quotes import fetch_market_quotes
from app.market_data.types import MarketDataUnavailableError

logger = logging.getLogger(__name__)


def _unavailable(*, reason: str) -> dict[str, object]:
    return {
        "available": False,
        "advancers": 0,
        "decliners": 0,
        "unchanged": 0,
        "total": 0,
        "advance_decline_ratio": None,
        "sector_performance": [],
        "as_of": None,
        "reason": reason,
    }


async def compute_market_breadth(db: Session) -> dict[str, object]:
    """Return the breadth snapshot of the EGX market."""
    try:
        snapshot = await fetch_market_quotes(db)
    except MarketDataUnavailableError as exc:
        logger.warning("Market breadth quotes unavailable: %s", exc)
        return _unavailable(reason=str(exc))

    if not snapshot.items:
        return _unavailable(reason="Empty quotes snapshot")

    advancers = decliners = unchanged = 0
    sector_changes: dict[str, list[float]] = {}

    for quote in snapshot.items:
        pct = quote.change_percent
        if pct is None:
            unchanged += 1
            continue
        if pct > 0:
            advancers += 1
        elif pct < 0:
            decliners += 1
        else:
            unchanged += 1

        sector = quote.sector or "غير محدد"
        sector_changes.setdefault(sector, []).append(pct)

    total = advancers + decliners + unchanged
    ad_ratio = advancers / decliners if decliners > 0 else (float("inf") if advancers > 0 else 1.0)

    sector_performance = [
        {
            "sector": sector,
            "avg_change_pct": round(mean(changes), 2),
            "symbols": len(changes),
        }
        for sector, changes in sector_changes.items()
    ]
    sector_performance.sort(key=lambda d: d["avg_change_pct"], reverse=True)

    return {
        "available": True,
        "advancers": advancers,
        "decliners": decliners,
        "unchanged": unchanged,
        "total": total,
        "advance_decline_ratio": round(ad_ratio, 2) if ad_ratio != float("inf") else None,
        "sector_performance": sector_performance,
        "as_of": snapshot.generated_at.isoformat(),
        "reason": None,
    }
