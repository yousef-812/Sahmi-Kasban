from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.models import MarketReport, MarketReportItem
from app.services.report_selection import (
    ELITE_SCORE_THRESHOLD,
    enrich_daily_report_selection,
)


def _analysis(*, ready: bool, failed_checks: list[str] | None = None) -> dict:
    return {
        "analysis_quality": {
            "engine_version": "core-v2.2",
            "elite_assessment": {
                "model_version": "elite-quality-v2.2",
                "engine_ready": ready,
                "readiness_score": 100 if ready else 86,
                "failed_checks": failed_checks or [],
            },
        }
    }


def test_report_selection_keeps_legacy_elite_name_and_adds_v23_context(
    db_session: Session,
) -> None:
    report = MarketReport(
        target_session_date=date(2026, 7, 30),
        status="complete",
        generated_at=datetime.now(UTC),
        source_snapshot={"source_session_date": "2026-07-29"},
        market_summary={
            "eligible_count": 200,
            "disclaimer": "old",
            "signals": {"BUY": 2, "WATCH": 1},
        },
    )
    db_session.add(report)
    db_session.flush()
    db_session.add_all(
        [
            MarketReportItem(
                report_id=report.id,
                ticker="ELITE",
                rank=1,
                score_bp=8400,
                payload={
                    "signal": "BUY",
                    "qualified": True,
                    "decision": "فرصة قوية",
                    "explanation": "تفاصيل أصلية",
                    "analysis": _analysis(ready=True),
                },
            ),
            MarketReportItem(
                report_id=report.id,
                ticker="OVEREXTENDED",
                rank=2,
                score_bp=8500,
                payload={
                    "signal": "BUY",
                    "qualified": True,
                    "analysis": _analysis(
                        ready=False,
                        failed_checks=["momentum_not_overextended"],
                    ),
                },
            ),
            MarketReportItem(
                report_id=report.id,
                ticker="WATCH",
                rank=3,
                score_bp=7600,
                payload={
                    "signal": "WATCH",
                    "qualified": True,
                    "analysis": _analysis(
                        ready=False,
                        failed_checks=["buy_signal", "directional_score"],
                    ),
                },
            ),
        ]
    )
    db_session.commit()

    enriched = enrich_daily_report_selection(db_session, report_id=report.id)
    rows = {
        item.ticker: item
        for item in db_session.query(MarketReportItem)
        .filter(MarketReportItem.report_id == report.id)
        .all()
    }

    elite = rows["ELITE"].payload
    assert elite["decision"] == "فرصة نخبوية"
    assert elite["opportunity_tier"] == "elite"
    assert elite["elite_profile"] == "legacy"
    assert elite["elite_opportunity"] is True
    assert elite["elite_score_threshold"] == ELITE_SCORE_THRESHOLD
    assert elite["elite_quality_score"] == 100
    assert elite["elite_gate_version"] == "elite-quality-v2.2"
    assert elite["elite_failed_checks"] == []
    assert elite["short_horizon"]["sessions"] == 5
    assert elite["trade_plan_context"]["horizon"] == "five_sessions"
    assert "التصنيف لا يضمن الربح" in elite["volatility_warning"]
    assert "تفاصيل أصلية" in elite["explanation"]
    assert elite["top_fraction_pct"] == 0.5

    conditional = rows["OVEREXTENDED"].payload
    assert conditional["decision"] == "شراء مشروط"
    assert conditional["opportunity_tier"] == "conditional_buy"
    assert conditional["elite_opportunity"] is False
    assert conditional["elite_failed_checks"] == ["momentum_not_overextended"]

    watch = rows["WATCH"].payload
    assert watch["decision"] == "مراقبة"
    assert watch["opportunity_tier"] == "watch"

    assert (
        enriched.market_summary["selection_model"]
        == "cross-sectional-top10-v2.3-regime-two-profile"
    )
    assert enriched.market_summary["opportunity_tiers"] == {
        "elite": 1,
        "elite_balanced": 0,
        "elite_aggressive": 0,
        "conditional_buy": 1,
        "watch": 1,
    }
    assert "نصف حجم المركز" in enriched.market_summary["disclaimer"]
    assert "قد لا يعرض التقرير" in enriched.market_summary["selection_notice"]
