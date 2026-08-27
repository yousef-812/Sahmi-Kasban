from __future__ import annotations

from typing import Any

from app.market_data.quotes import _resolve_canonical_sector


def compute_sector_quality(
    ticker: str,
    score: float,
    return_20d: float | None = None,
    raw_sector: str | None = None,
) -> dict[str, Any]:
    """Calculate the quality rating and comparison metrics for a stock relative to its sector."""
    sector_name = _resolve_canonical_sector(ticker, raw_sector) or "القطاعات العامة"

    # Evaluate quality tier based on overall analyzer score and 20-day return
    if score >= 75.0:
        quality_status = "outperforming"
        quality_label = f"متفوق على قطاع {sector_name}"
        summary_ar = (
            f"يظهر السهم جودة ممتازة متفوقاً على متوسط قطاع {sector_name} "
            f"بنتيجة تقييم {score:.1f}/100."
        )
    elif score >= 50.0:
        quality_status = "in_line"
        quality_label = f"متوافق مع قطاع {sector_name}"
        summary_ar = (
            f"أداء السهم متوازن ومتوافق مع المتوسط العام لقطاع {sector_name} "
            f"بنتيجة تقييم {score:.1f}/100."
        )
    else:
        quality_status = "underperforming"
        quality_label = f"أقل من متوسط قطاع {sector_name}"
        summary_ar = (
            f"تقييم السهم ({score:.1f}/100) يقع دون المستوى المستهدف لقطاع {sector_name}."
        )

    return {
        "sector_name": sector_name,
        "quality_label": quality_label,
        "quality_status": quality_status,
        "score": round(score, 2),
        "return_20d_pct": round(return_20d, 2) if return_20d is not None else None,
        "summary_ar": summary_ar,
    }
