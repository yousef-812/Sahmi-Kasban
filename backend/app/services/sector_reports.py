"""Sector leaderboard computed from scanner snapshots (WP-06) + sector quality.

The leaderboard of ``GET /reports/sectors/{sector_id}/leaderboard`` is derived
from the newest ``technical`` scanner snapshots of the symbols belonging to the
requested sector. Each row carries the real technical score, rating and payload
metrics of one symbol; the summary aggregates those rows and attaches the
quality rating produced by :mod:`app.services.sector_quality`.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.market_data.egx_symbols import EGX_ARABIC_NAMES
from app.services.scanner import get_scanner_items
from app.services.sector_quality import compute_sector_quality

LEADERBOARD_SCANNER_KIND = "technical"

AVAILABLE_SECTORS: dict[str, str] = {
    "banking": "قطاع البنوك",
    "real_estate": "قطاع العقارات والأراضي",
    "technology": "قطاع التكنولوجيا والاتصالات",
    "financial_services": "قطاع الخدمات المالية والسيولة",
    "basic_resources": "قطاع الموارد الأساسية والتعدين",
    "healthcare": "قطاع الرعاية الصحية والأدوية",
}

SECTOR_CANONICAL_SECTOR: dict[str, str] = {
    "banking": "البنوك",
    "real_estate": "العقارات",
    "technology": "الاتصالات والتكنولوجيا",
    "financial_services": "الخدمات المالية",
    "basic_resources": "موارد أساسية",
    "healthcare": "الرعاية الصحية",
}

SIGNAL_LABELS: dict[str, str] = {"buy": "شراء", "sell": "بيع", "neutral": "محايد"}


def _payload_number(item: dict[str, Any], key: str) -> float | None:
    value = item.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _score_value(item: dict[str, Any]) -> float | None:
    score = item.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return None
    return float(score)


async def build_sector_leaderboard(db: Session, *, sector_code: str) -> dict[str, Any]:
    """Compute the leaderboard of ``sector_code`` from stored technical snapshots.

    Ordering is deterministic: score descending, symbols without a score last,
    and the ticker (ascending) as the tiebreak.
    """
    canonical_sector = SECTOR_CANONICAL_SECTOR[sector_code]
    scanner_items = await get_scanner_items(
        db,
        kind=LEADERBOARD_SCANNER_KIND,
        sector=canonical_sector,
    )

    entries: list[dict[str, Any]] = []
    for item in scanner_items:
        symbol = str(item.get("symbol") or "")
        rating = str(item.get("rating") or "neutral")
        company_name = item.get("nameAr") or EGX_ARABIC_NAMES.get(symbol) or symbol
        entries.append(
            {
                "ticker": symbol,
                "company_name": str(company_name),
                "rank": 0,
                "score": _score_value(item),
                "rating": rating,
                "signal": SIGNAL_LABELS.get(rating, "محايد"),
                "atr": _payload_number(item, "atr14"),
                "relative_volume": _payload_number(item, "relativeVolume20"),
                "rsi14": _payload_number(item, "rsi14"),
                "performance_20d_pct": _payload_number(item, "performance20d"),
                "as_of": str(item.get("as_of") or ""),
            }
        )

    entries.sort(key=lambda entry: (entry["score"] is None, -(entry["score"] or 0.0), entry["ticker"]))
    for rank, entry in enumerate(entries, start=1):
        entry["rank"] = rank

    scores = [entry["score"] for entry in entries if entry["score"] is not None]
    average_score = round(sum(scores) / len(scores), 2) if scores else None
    buy_count = sum(1 for entry in entries if entry["rating"] == "buy")
    sell_count = sum(1 for entry in entries if entry["rating"] == "sell")
    neutral_count = sum(1 for entry in entries if entry["rating"] == "neutral")

    best_ticker = entries[0]["ticker"] if entries else None
    worst_ticker = entries[-1]["ticker"] if entries else None

    momentum = [
        entry["performance_20d_pct"]
        for entry in entries
        if entry["performance_20d_pct"] is not None
    ]
    sector_momentum = round(sum(momentum) / len(momentum), 2) if momentum else None
    quality = (
        compute_sector_quality(
            ticker=best_ticker or sector_code,
            score=average_score if average_score is not None else 0.0,
            return_20d=sector_momentum,
            sector_momentum_pct=sector_momentum,
            raw_sector=canonical_sector,
        )
        if entries
        else None
    )

    return {
        "sector_code": sector_code,
        "sector_name": AVAILABLE_SECTORS[sector_code],
        "leader_ticker": best_ticker or "",
        "degraded": not entries,
        "summary": {
            "scanner_kind": LEADERBOARD_SCANNER_KIND,
            "symbol_count": len(entries),
            "average_score": average_score,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "neutral_count": neutral_count,
            "best_ticker": best_ticker,
            "worst_ticker": worst_ticker,
            "quality": quality,
        },
        "items": entries,
    }
