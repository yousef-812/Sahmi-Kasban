from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MarketReport, MarketReportItem

ELITE_SCORE_THRESHOLD = 80.0
SHORT_HORIZON_SESSIONS = 5
_AGGRESSIVE_SELECTION_REGIMES = {"broad_bullish", "speculative_bullish"}


@dataclass(frozen=True, slots=True)
class OpportunityClassification:
    tier: str
    decision: str
    elite: bool
    profile: str
    top_fraction_pct: float
    quality_score: float
    gate_version: str
    failed_checks: tuple[str, ...]
    note: str
    volatility_warning: str | None
    position_multiplier: float


def _number(value: object, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except (TypeError, ValueError):
        return default


def _mapping(value: object) -> dict:
    return dict(value) if isinstance(value, dict) else {}


def _elite_assessment(payload: dict) -> dict:
    analysis = _mapping(payload.get("analysis"))
    quality = _mapping(analysis.get("analysis_quality"))
    return _mapping(quality.get("elite_assessment"))


def _market_engine_details(payload: dict) -> dict:
    analysis = _mapping(payload.get("analysis"))
    engines = _mapping(analysis.get("engines"))
    market = _mapping(engines.get("market_environment"))
    return _mapping(market.get("details"))


def _failed_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value if str(item).strip())


def _selection_regime(items: list[MarketReportItem]) -> dict[str, object]:
    if not items:
        return {
            "profile": "unknown",
            "model_version": "top-basket-regime-v2.3",
            "sample_size": 0,
        }

    bullish = bearish = high_volatility = buy = 0
    for item in items:
        payload = _mapping(item.payload)
        details = _market_engine_details(payload)
        regime = str(details.get("regime", ""))
        profile = str(details.get("regime_profile", ""))
        if regime == "bullish":
            bullish += 1
        elif regime == "bearish":
            bearish += 1
        if (
            _number(details.get("annualized_volatility_pct")) >= 65
            or "speculative" in profile
            or "volatile" in profile
        ):
            high_volatility += 1
        if str(payload.get("signal", "")).upper() == "BUY":
            buy += 1

    count = len(items)
    bullish_share = bullish / count
    bearish_share = bearish / count
    high_volatility_share = high_volatility / count
    buy_share = buy / count
    if bearish_share >= 0.50 or buy_share < 0.20:
        profile = "risk_off"
    elif bullish_share >= 0.70 and high_volatility_share >= 0.30:
        profile = "speculative_bullish"
    elif bullish_share >= 0.60 and buy_share >= 0.50:
        profile = "broad_bullish"
    elif bullish_share >= 0.40:
        profile = "selective_bullish"
    else:
        profile = "mixed_rotation"
    return {
        "profile": profile,
        "model_version": "top-basket-regime-v2.3",
        "sample_size": count,
        "bullish_share_pct": round(bullish_share * 100.0, 2),
        "bearish_share_pct": round(bearish_share * 100.0, 2),
        "high_volatility_share_pct": round(high_volatility_share * 100.0, 2),
        "buy_share_pct": round(buy_share * 100.0, 2),
        "scope": "top-ranked basket, not a broad EGX index",
    }


def classify_report_item(
    item: MarketReportItem,
    *,
    eligible_count: int,
    selection_regime: str = "unknown",
) -> OpportunityClassification:
    payload = item.payload if isinstance(item.payload, dict) else {}
    signal = str(payload.get("signal", "WATCH")).upper()
    qualified = bool(payload.get("qualified", False))
    score = item.score_bp / 100.0
    top_fraction_pct = round(item.rank / max(eligible_count, 1) * 100.0, 2)
    assessment = _elite_assessment(payload)
    gate_version = str(assessment.get("model_version", "elite-quality-unavailable"))
    quality_score = _number(assessment.get("readiness_score"))
    failed_checks = _failed_tuple(assessment.get("failed_checks"))
    profile = "none"
    position_multiplier = 1.0

    if gate_version.startswith("elite-quality-v2.3"):
        balanced_ready = assessment.get("balanced_ready") is True
        aggressive_ready = assessment.get("aggressive_ready") is True
        if balanced_ready:
            profile = "balanced"
            quality_score = _number(
                assessment.get("balanced_readiness_score"),
                quality_score,
            )
        elif aggressive_ready and selection_regime in _AGGRESSIVE_SELECTION_REGIMES:
            profile = "aggressive"
            quality_score = _number(
                assessment.get("aggressive_readiness_score"),
                quality_score,
            )
            position_multiplier = min(
                0.5,
                _number(assessment.get("recommended_position_multiplier"), 0.5),
            )
        else:
            failed_checks = tuple(
                [
                    f"balanced:{name}"
                    for name in _failed_tuple(assessment.get("balanced_failed_checks"))
                ]
                + [
                    f"aggressive:{name}"
                    for name in _failed_tuple(assessment.get("aggressive_failed_checks"))
                ]
            )
            if aggressive_ready and selection_regime not in _AGGRESSIVE_SELECTION_REGIMES:
                failed_checks += ("aggressive:selection_regime_not_supportive",)
    elif assessment.get("engine_ready") is True:
        profile = "legacy"

    elite = (
        item.rank <= 10
        and signal == "BUY"
        and qualified
        and score >= ELITE_SCORE_THRESHOLD
        and profile != "none"
    )
    if elite:
        if profile == "aggressive":
            decision = "فرصة نخبوية هجومية"
            note = (
                "اختراق قوي مؤكد بالحجم والسيولة اجتاز مسار Core v2.3 الهجومي. "
                "التصنيف يسمح بتذبذب أعلى مقابل حجم مركز أصغر وإدارة أسرع."
            )
            warning = (
                "فرصة هجومية عالية التذبذب؛ استخدم نصف حجم المركز المقترح، "
                "ولا تطارد السعر بعد فجوة أو اندفاع جديد."
            )
        elif profile == "balanced":
            decision = "فرصة نخبوية متوازنة"
            note = (
                "فرصة نخبوية اجتازت ترتيب اليوم ومسار Core v2.3 المتوازن "
                "بحدود تذبذب ومخاطر متكيفة مع سيولة السهم."
            )
            warning = (
                "الفرصة المتوازنة لا تضمن الربح؛ التزم بوقف الخسارة وحجم "
                "المركز ولا تعتبر التصنيف بديلًا عن المتابعة."
            )
        else:
            decision = "فرصة نخبوية"
            note = "فرصة نخبوية اجتازت بوابات الجودة السابقة."
            warning = "التصنيف لا يضمن الربح؛ التزم بإدارة المخاطر."
        return OpportunityClassification(
            tier="elite",
            decision=decision,
            elite=True,
            profile=profile,
            top_fraction_pct=top_fraction_pct,
            quality_score=quality_score,
            gate_version=gate_version,
            failed_checks=(),
            note=note,
            volatility_warning=warning,
            position_multiplier=position_multiplier,
        )

    if signal == "BUY":
        return OpportunityClassification(
            tier="conditional_buy",
            decision="شراء مشروط",
            elite=False,
            profile="none",
            top_fraction_pct=top_fraction_pct,
            quality_score=quality_score,
            gate_version=gate_version,
            failed_checks=failed_checks,
            note=(
                "إشارة شراء جيدة، لكنها لم تجتز مسارًا كاملًا من مساري الفرصة "
                "النخبوية؛ راقب الاختراق والتذبذب والسيولة وشروط الدخول."
            ),
            volatility_warning=None,
            position_multiplier=1.0,
        )
    return OpportunityClassification(
        tier="watch",
        decision="مراقبة",
        elite=False,
        profile="none",
        top_fraction_pct=top_fraction_pct,
        quality_score=quality_score,
        gate_version=gate_version,
        failed_checks=failed_checks,
        note=(
            "السهم ظهر ضمن أعلى ترتيب اليوم، لكن شروط الشراء غير مكتملة؛ "
            "يعرض للمراقبة ولا يعامل كتوصية دخول."
        ),
        volatility_warning=None,
        position_multiplier=1.0,
    )


def _adjusted_trade_plan(payload: dict, multiplier: float) -> dict | None:
    analysis = _mapping(payload.get("analysis"))
    plan = _mapping(analysis.get("trade_plan"))
    if not plan:
        return None
    adjusted = dict(plan)
    adjusted["position_size"] = int(_number(plan.get("position_size")) * multiplier)
    adjusted["position_value"] = round(
        _number(plan.get("position_value")) * multiplier,
        2,
    )
    adjusted["risk_amount"] = round(_number(plan.get("risk_amount")) * multiplier, 2)
    adjusted["position_multiplier"] = multiplier
    return adjusted


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
    regime = _selection_regime(items)
    regime_profile = str(regime["profile"])
    tier_counts = {
        "elite": 0,
        "elite_balanced": 0,
        "elite_aggressive": 0,
        "conditional_buy": 0,
        "watch": 0,
    }

    for item in items:
        payload = dict(item.payload or {})
        classification = classify_report_item(
            item,
            eligible_count=eligible_count,
            selection_regime=regime_profile,
        )
        tier_counts[classification.tier] += 1
        if classification.profile == "balanced":
            tier_counts["elite_balanced"] += 1
        elif classification.profile == "aggressive":
            tier_counts["elite_aggressive"] += 1

        original_explanation = str(payload.get("explanation", "")).strip()
        context_parts = [classification.note]
        if classification.volatility_warning:
            context_parts.append(classification.volatility_warning)
        context_parts.append(
            "الخطة محسوبة لأفق خمس جلسات وتستخدم أهدافًا أقرب مبنية على ATR."
        )
        if original_explanation:
            context_parts.append(original_explanation)

        payload.update(
            {
                "decision": classification.decision,
                "opportunity_tier": classification.tier,
                "elite_profile": classification.profile,
                "elite_opportunity": classification.elite,
                "elite_score_threshold": ELITE_SCORE_THRESHOLD,
                "elite_quality_score": round(classification.quality_score, 2),
                "elite_gate_version": classification.gate_version,
                "elite_failed_checks": list(classification.failed_checks),
                "selection_regime": regime,
                "selection_rank": item.rank,
                "eligible_universe_size": eligible_count,
                "top_fraction_pct": classification.top_fraction_pct,
                "selection_note": classification.note,
                "recommended_position_multiplier": classification.position_multiplier,
                "adjusted_trade_plan": _adjusted_trade_plan(
                    payload,
                    classification.position_multiplier,
                ),
                "short_horizon": {
                    "sessions": SHORT_HORIZON_SESSIONS,
                    "label": "خطة ومتابعة بعد 5 جلسات تداول",
                    "purpose": "قياس جودة الاختيار وإدارة صفقة قصيرة الأفق",
                },
                "trade_plan_context": {
                    "horizon": "five_sessions",
                    "label": "خطة ATR قصيرة الأفق",
                    "note": "الأهداف 1R و1.75R؛ الهجومية قد تستخدم 1.25R و2R.",
                },
                "volatility_warning": classification.volatility_warning,
                "explanation": "\n\n".join(context_parts),
            }
        )
        item.payload = payload

    summary.update(
        {
            "title": "أفضل 10 فرص مرتبة للجلسة القادمة وفق Core v2.3",
            "ranking_scope": (
                "ترتيب يومي مع مسار نخبوية متوازن ومسار هجومي مشروط بحالة السوق"
            ),
            "selection_model": "cross-sectional-top10-v2.3-regime-two-profile",
            "selection_regime": regime,
            "short_horizon_sessions": SHORT_HORIZON_SESSIONS,
            "elite_score_threshold": ELITE_SCORE_THRESHOLD,
            "elite_gate_version": "elite-quality-v2.3-regime-aware",
            "opportunity_tiers": tier_counts,
            "selection_notice": (
                "قد لا يعرض التقرير فرصة نخبوية. المسار الهجومي لا يتفعل إلا "
                "مع حالة سوق داعمة واختراق وحجم وسيولة مؤكدة."
            ),
            "disclaimer": (
                "هذا ترتيب تحليلي وليس توصية شراء أو بيع. الفرصة المتوازنة "
                "تستهدف ضبط المخاطر، والهجومية أعلى تذبذبًا وتستخدم نصف حجم المركز."
            ),
        }
    )
    report.market_summary = summary
    db.commit()
    db.refresh(report)
    return report
