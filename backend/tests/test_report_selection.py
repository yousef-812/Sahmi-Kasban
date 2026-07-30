from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.models import MarketReport, MarketReportItem
from app.services.report_selection import (
    ELITE_SCORE_THRESHOLD,
    enrich_daily_report_selection,
)


def test_report_selection_separates_elite_conditional_and_watch(
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
                },
            ),
            MarketReportItem(
                report_id=report.id,
                ticker="CONDITIONAL",
                rank=2,
                score_bp=7900,
                payload={"signal": "BUY", "qualified": True},
            ),
            MarketReportItem(
                report_id=report.id,
                ticker="WATCH",
                rank=3,
                score_bp=7600,
                payload={"signal": "WATCH", "qualified": True},
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
    assert elite["elite_opportunity"] is True
    assert elite["elite_score_threshold"] == ELITE_SCORE_THRESHOLD
    assert elite["short_horizon"]["sessions"] == 5
    assert elite["trade_plan_context"]["horizon"] == "extended"
    assert "أعلى تذبذبًا" in elite["volatility_warning"]
    assert "تفاصيل أصلية" in elite["explanation"]
    assert elite["top_fraction_pct"] == 0.5

    conditional = rows["CONDITIONAL"].payload
    assert conditional["decision"] == "شراء مشروط"
    assert conditional["opportunity_tier"] == "conditional_buy"
    assert conditional["elite_opportunity"] is False

    watch = rows["WATCH"].payload
    assert watch["decision"] == "مراقبة"
    assert watch["opportunity_tier"] == "watch"

    assert enriched.market_summary["selection_model"] == "cross-sectional-top10-v1"
    assert enriched.market_summary["opportunity_tiers"] == {
        "elite": 1,
        "conditional_buy": 1,
        "watch": 1,
    }
    assert "خمس جلسات" in enriched.market_summary["disclaimer"]
