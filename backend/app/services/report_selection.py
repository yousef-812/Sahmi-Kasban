from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MarketReport, MarketReportItem

ELITE_SCORE_THRESHOLD = 80.0
SHORT_HORIZON_SESSIONS = 5


@dataclass(frozen=True, slots=True)
class OpportunityClassification:
    tier: str
    decision: str
    elite: bool
    top_fraction_pct: float
    note: str
    volatility_warning: str | None


def _number(value: object, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def classify_report_item(
    item: MarketReportItem,
    *,
    eligible_count: int,
) -> OpportunityClassification:
    payload = item.payload if isinstance(item.payload, dict) else {}
    signal = str(payload.get("signal", "WATCH")).upper()
    qualified = bool(payload.get("qualified", False))
    score = item.score_bp / 100.0
    top_fraction_pct = round(item.rank / max(eligible_count, 1) * 100.0, 2)
    elite = (
        item.rank <= 10
        and signal == "BUY"
        and qualified
        and score >= ELITE_SCORE_THRESHOLD
    )

    if elite:
        return OpportunityClassification(
            tier="elite",
            decision="فرصة نخبوية",
            elite=True,
            top_fraction_pct=top_fraction_pct,
            note=(
                "اختيار نخبوِي ضمن أعلى ترتيب يومي وبدرجة لا تقل عن 80. "
                "التقييم القصير يتابع خمس جلسات، وليس وعدًا بتحقيق أهداف السعر."
            ),
            volatility_warning=(
                "الفرص الأعلى ترتيبًا قد تحقق حركة أكبر، لكنها قد تتعرض أيضًا "
                "لتذبذب وهبوط مؤقت أقوى؛ التزم بوقف الخسارة وحجم المركز."
            ),
        )
    if signal == "BUY":
        return OpportunityClassification(
            tier="conditional_buy",
            decision="شراء مشروط",
            elite=False,
            top_fraction_pct=top_fraction_pct,
            note=(
                "إشارة شراء مشروطة ضمن أفضل ترتيب اليوم، لكنها ليست ضمن طبقة "
                "الفرص النخبوية المثبتة بالدرجة. راقب شروط الدخول والمخاطر."
            ),
            volatility_warning=None,
        )
    return OpportunityClassification(
        tier="watch",
        decision="مراقبة",
        elite=False,
        top_fraction_pct=top_fraction_pct,
        note=(
            "السهم ظهر ضمن أعلى ترتيب اليوم، لكن شروط الشراء غير مكتملة؛ "
            "يعرض للمراقبة ولا يعامل كتوصية دخول."
        ),
        volatility_warning=None,
    )


def enrich_daily_report_selection(
    db: Session,
    *,
    report_id: UUID,
) -> MarketReport:
    report = db.get(MarketReport, report_id)
    if report is None:
        raise LookupError("Market report was not found for selection enrichment")

    items = list(
        db.scalars(
            select(MarketReportItem)
            .where(MarketReportItem.report_id == report.id)
            .order_by(MarketReportItem.rank.asc())
        ).all()
    )
    summary = dict(report.market_summary or {})
    reported_eligible = int(_number(summary.get("eligible_count"), len(items)))
    eligible_count = max(reported_eligible, len(items))
    tier_counts = {"elite": 0, "conditional_buy": 0, "watch": 0}

    for item in items:
        payload = dict(item.payload or {})
        classification = classify_report_item(item, eligible_count=eligible_count)
        tier_counts[classification.tier] += 1

        original_explanation = str(payload.get("explanation", "")).strip()
        context_parts = [classification.note]
        if classification.volatility_warning:
            context_parts.append(classification.volatility_warning)
        context_parts.append(
            "أفق ترتيب التقرير خمس جلسات تداول؛ أما الدخول ووقف الخسارة "
            "والهدفان فهي خطة تداول ممتدة وقد تحتاج مدة أطول."
        )
        if original_explanation:
            context_parts.append(original_explanation)

        payload.update(
            {
                "decision": classification.decision,
                "opportunity_tier": classification.tier,
                "elite_opportunity": classification.elite,
                "elite_score_threshold": ELITE_SCORE_THRESHOLD,
                "selection_rank": item.rank,
                "eligible_universe_size": eligible_count,
                "top_fraction_pct": classification.top_fraction_pct,
                "selection_note": classification.note,
                "short_horizon": {
                    "sessions": SHORT_HORIZON_SESSIONS,
                    "label": "متابعة قصيرة بعد 5 جلسات تداول",
                    "purpose": "قياس جودة الترتيب والاتجاه النسبي",
                },
                "trade_plan_context": {
                    "horizon": "extended",
                    "label": "خطة تداول ممتدة",
                    "note": "الأهداف ليست متوقعة بالضرورة داخل خمس جلسات.",
                },
                "volatility_warning": classification.volatility_warning,
                "explanation": "\n\n".join(context_parts),
            }
        )
        item.payload = payload

    summary.update(
        {
            "title": "أفضل 10 فرص مرتبة للجلسة القادمة وفق Core v2.1",
            "ranking_scope": "ترتيب يومي انتقائي لأفضل الأسهم المؤهلة",
            "selection_model": "cross-sectional-top10-v1",
            "short_horizon_sessions": SHORT_HORIZON_SESSIONS,
            "elite_score_threshold": ELITE_SCORE_THRESHOLD,
            "opportunity_tiers": tier_counts,
            "selection_notice": (
                "قوة التقرير في ترتيب أفضل الفرص، وليس في اعتبار كل إشارة BUY "
                "فرصة متساوية الجودة."
            ),
            "disclaimer": (
                "هذا ترتيب تحليلي لدعم القرار وليس توصية شراء أو بيع. "
                "الفرصة النخبوية تعني أعلى ترتيب مع درجة 80 فأكثر، وقد تكون "
                "أعلى تذبذبًا. تقييم التقرير القصير بعد خمس جلسات، بينما أهداف "
                "خطة التداول قد تحتاج مدة أطول."
            ),
        }
    )
    report.market_summary = summary
    db.commit()
    db.refresh(report)
    return report
