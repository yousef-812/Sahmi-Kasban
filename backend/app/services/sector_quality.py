from __future__ import annotations

from typing import Any

from app.market_data.quotes import _resolve_canonical_sector


def compute_sector_quality(
    ticker: str,
    score: float,
    return_20d: float | None = None,
    sector_momentum_pct: float | None = None,
    raw_sector: str | None = None,
) -> dict[str, Any]:
    """Calculate the quality rating, sector trend (صاعد/هابط), and comparison metrics for a stock relative to its sector."""
    sector_name = _resolve_canonical_sector(ticker, raw_sector) or "القطاعات العامة"

    # Evaluate sector trend (صاعد / هابط / عرضي)
    if sector_momentum_pct is not None:
        if sector_momentum_pct >= 0.5:
            sector_trend = "bullish"
            sector_trend_ar = "صاعد 📈"
            trend_desc = f"في اتجاه صاعد (+{sector_momentum_pct:.1f}%)"
        elif sector_momentum_pct <= -0.5:
            sector_trend = "bearish"
            sector_trend_ar = "هابط 📉"
            trend_desc = f"في اتجاه هابط ({sector_momentum_pct:.1f}%)"
        else:
            sector_trend = "neutral"
            sector_trend_ar = "عرضي ➡️"
            trend_desc = f"في اتجاه عرضي ({sector_momentum_pct:.1f}%)"
    else:
        if return_20d is not None and return_20d >= 1.0:
            sector_trend = "bullish"
            sector_trend_ar = "صاعد 📈"
            trend_desc = "في اتجاه صاعد"
        elif return_20d is not None and return_20d <= -1.0:
            sector_trend = "bearish"
            sector_trend_ar = "هابط 📉"
            trend_desc = "في اتجاه هابط"
        else:
            sector_trend = "neutral"
            sector_trend_ar = "مستقر ➡️"
            trend_desc = "في اتجاه مستقر"

    # Evaluate quality tier based on overall analyzer score and return
    if score >= 75.0:
        quality_status = "outperforming"
        quality_label = f"متفوق على قطاع {sector_name}"
        summary_ar = (
            f"يظهر السهم جودة ممتازة متفوقاً على قطاع {sector_name} "
            f"({trend_desc}) بنتيجة تقييم {score:.1f}/100."
        )
    elif score >= 50.0:
        quality_status = "in_line"
        quality_label = f"متوافق مع قطاع {sector_name}"
        summary_ar = (
            f"أداء السهم متوازن ومتوافق مع حركة قطاع {sector_name} "
            f"({trend_desc}) بنتيجة تقييم {score:.1f}/100."
        )
    else:
        quality_status = "underperforming"
        quality_label = f"أقل من متوسط قطاع {sector_name}"
        summary_ar = f"تقييم السهم ({score:.1f}/100) يقع دون المستهدف لقطاع {sector_name} ({trend_desc})."

    return {
        "sector_name": sector_name,
        "quality_label": quality_label,
        "quality_status": quality_status,
        "sector_trend": sector_trend,
        "sector_trend_ar": sector_trend_ar,
        "sector_momentum_pct": round(sector_momentum_pct, 2) if sector_momentum_pct is not None else None,
        "score": round(score, 2),
        "return_20d_pct": round(return_20d, 2) if return_20d is not None else None,
        "summary_ar": summary_ar,
    }
