from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.models import MarketReport, MarketReportItem
from app.services.report_selection import enrich_daily_report_selection


def _payload(*, profile: str, volatility: float) -> dict:
    balanced = profile == "balanced"
    aggressive = profile == "aggressive"
    return {
        "signal": "BUY",
        "qualified": True,
        "analysis": {
            "analysis_quality": {
                "engine_version": "core-v2.3",
                "elite_assessment": {
                    "model_version": "elite-quality-v2.3-regime-aware",
                    "engine_ready": balanced or aggressive,
                    "selected_profile": profile,
                    "balanced_ready": balanced,
                    "aggressive_ready": aggressive,
                    "readiness_score": 100,
                    "balanced_readiness_score": 100 if balanced else 82,
                    "aggressive_readiness_score": 100 if aggressive else 70,
                    "recommended_position_multiplier": 0.5 if aggressive else 1.0,
                    "failed_checks": [],
                    "balanced_failed_checks": [] if balanced else ["atr_controlled"],
                    "aggressive_failed_checks": [] if aggressive else ["breakout_confirmed"],
                },
            },
            "engines": {
                "market_environment": {
                    "details": {
                        "model_version": "market-regime-v2.3",
                        "regime": "bullish",
                        "regime_profile": (
                            "speculative_bullish" if volatility >= 65 else "trend_bullish"
                        ),
                        "annualized_volatility_pct": volatility,
                    }
                }
            },
            "trade_plan": {
                "position_size": 100,
                "position_value": 20_000.0,
                "risk_amount": 1_000.0,
                "reward_risk_1": 1.25 if aggressive else 1.0,
                "reward_risk_2": 2.0 if aggressive else 1.75,
            },
        },
        "explanation": "تفاصيل أصلية",
    }


def test_v23_report_disables_unvalidated_public_elite_profiles(
    db_session: Session,
) -> None:
    report = MarketReport(
        target_session_date=date(2026, 8, 2),
        status="complete",
        generated_at=datetime.now(UTC),
        source_snapshot={"source_session_date": "2026-07-30"},
        market_summary={"eligible_count": 200},
    )
    db_session.add(report)
    db_session.flush()
    db_session.add_all(
        [
            MarketReportItem(
                report_id=report.id,
                ticker="BAL",
                rank=1,
                score_bp=8600,
                payload=_payload(profile="balanced", volatility=45),
            ),
            MarketReportItem(
                report_id=report.id,
                ticker="AGG",
                rank=2,
                score_bp=8500,
                payload=_payload(profile="aggressive", volatility=75),
            ),
            MarketReportItem(
                report_id=report.id,
                ticker="COND",
                rank=3,
                score_bp=8300,
                payload=_payload(profile="none", volatility=72),
            ),
        ]
    )
    db_session.commit()

    enriched = enrich_daily_report_selection(db_session, report_id=report.id)
    rows = {
        item.ticker: item.payload
        for item in db_session.query(MarketReportItem)
        .filter(MarketReportItem.report_id == report.id)
        .all()
    }

    assert enriched.market_summary["selection_regime"]["profile"] == "speculative_bullish"

    assert rows["BAL"]["decision"] == "شراء مشروط بجودة أعلى"
    assert rows["BAL"]["elite_profile"] == "balanced_candidate"
    assert rows["BAL"]["elite_opportunity"] is False
    assert rows["BAL"]["recommended_position_multiplier"] == 1.0

    assert rows["AGG"]["decision"] == "شراء مشروط"
    assert rows["AGG"]["elite_profile"] == "none"
    assert rows["AGG"]["elite_opportunity"] is False
    assert "aggressive:disabled_pending_validation" in rows["AGG"]["elite_failed_checks"]
    assert rows["AGG"]["recommended_position_multiplier"] == 1.0
    assert rows["AGG"]["adjusted_trade_plan"]["position_size"] == 100

    assert rows["COND"]["decision"] == "شراء مشروط"
    assert rows["COND"]["elite_opportunity"] is False
    assert enriched.market_summary["public_elite_labels_enabled"] is False
    assert enriched.market_summary["aggressive_profile_enabled"] is False
    assert enriched.market_summary["opportunity_tiers"] == {
        "conditional_buy_high_quality": 1,
        "conditional_buy": 2,
        "watch": 0,
        "elite": 0,
        "elite_balanced": 0,
        "elite_aggressive": 0,
    }
