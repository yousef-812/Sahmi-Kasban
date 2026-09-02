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


def test_report_selection_uses_production_safe_public_labels(
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
                ticker="READY",
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
        for item in db_session.query(MarketReportItem).filter(MarketReportItem.report_id == report.id).all()
    }

    ready = rows["READY"].payload
    assert ready["decision"] == "شراء مشروط بجودة أعلى"
    assert ready["opportunity_tier"] == "conditional_buy_high_quality"
    assert ready["elite_profile"] == "balanced_candidate"
    assert ready["elite_opportunity"] is False
    assert ready["elite_score_threshold"] == ELITE_SCORE_THRESHOLD
    assert ready["elite_quality_score"] == 100
    assert ready["elite_gate_version"] == "elite-quality-v2.2"
    assert ready["elite_failed_checks"] == []
    assert ready["short_horizon"]["sessions"] == 5
    assert ready["trade_plan_context"]["horizon"] == "five_sessions"
    assert "لا يضمن التفوق" in ready["volatility_warning"]
    assert "تفاصيل أصلية" in ready["explanation"]
    assert ready["top_fraction_pct"] == 0.5

    conditional = rows["OVEREXTENDED"].payload
    assert conditional["decision"] == "شراء مشروط"
    assert conditional["opportunity_tier"] == "conditional_buy"
    assert conditional["elite_opportunity"] is False
    assert conditional["elite_failed_checks"] == ["momentum_not_overextended"]

    watch = rows["WATCH"].payload
    assert watch["decision"] == "مراقبة"
    assert watch["opportunity_tier"] == "watch"

    assert enriched.market_summary["selection_model"] == "cross-sectional-top10-v2.5-regime-adaptive"
    assert enriched.market_summary["opportunity_tiers"] == {
        "conditional_buy_high_quality": 1,
        "conditional_buy": 1,
        "watch": 1,
        "elite": 0,
        "elite_balanced": 0,
        "elite_aggressive": 0,
    }
    assert enriched.market_summary["public_elite_labels_enabled"] is False
    assert enriched.market_summary["aggressive_profile_enabled"] is False
    assert "ليس توصية" in enriched.market_summary["disclaimer"]
    assert "قد لا يعرض التقرير فرصة نخبوية" in enriched.market_summary["selection_notice"]


def test_enrich_daily_report_selection_is_idempotent(
    db_session: Session,
) -> None:
    report = MarketReport(
        target_session_date=date(2026, 7, 31),
        status="complete",
        generated_at=datetime.now(UTC),
        source_snapshot={"source_session_date": "2026-07-30"},
        market_summary={"eligible_count": 50, "disclaimer": "test"},
    )
    db_session.add(report)
    db_session.flush()
    db_session.add(
        MarketReportItem(
            report_id=report.id,
            ticker="TEST",
            rank=1,
            score_bp=9000,
            payload={
                "signal": "BUY",
                "qualified": True,
                "explanation": "شرح خاص بالسهم فقط.",
                "analysis": _analysis(ready=True),
            },
        )
    )
    db_session.commit()

    enrich_daily_report_selection(db_session, report_id=report.id)
    first_item = db_session.query(MarketReportItem).filter(MarketReportItem.report_id == report.id).first()
    first_explanation = first_item.payload["explanation"]

    enrich_daily_report_selection(db_session, report_id=report.id)
    second_item = db_session.query(MarketReportItem).filter(MarketReportItem.report_id == report.id).first()
    second_explanation = second_item.payload["explanation"]

    assert first_explanation == second_explanation
    assert second_explanation.count("الخطة محسوبة لأفق خمس جلسات") == 1
    assert second_explanation.count("شرح خاص بالسهم فقط.") == 1
