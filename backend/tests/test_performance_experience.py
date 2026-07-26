from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    CommunityAdminEvent,
    MarketReport,
    MarketReportEvaluation,
    MarketReportItem,
    MarketReportItemOutcome,
    MarketReportOutcomeRevision,
    User,
)
from app.services.performance_experience import (
    correct_performance_outcome,
    export_performance_csv,
    get_performance_report_detail,
    get_performance_summary,
    list_delayed_performance_reports,
    list_performance_reports,
)


def _moment() -> datetime:
    return datetime(2026, 7, 26, 18, 0, tzinfo=ZoneInfo("Africa/Cairo"))


def _create_report(
    db: Session,
    *,
    target_date: date,
    values: list[int | None],
    evaluation_status: str,
) -> tuple[MarketReport, list[MarketReportItemOutcome]]:
    report = MarketReport(
        target_session_date=target_date,
        status="complete",
        generated_at=datetime(2026, 7, 20, 15, 0, tzinfo=UTC),
        source_snapshot={"source_session_date": "2026-07-19"},
        market_summary={},
    )
    db.add(report)
    db.flush()
    evaluation = MarketReportEvaluation(
        report_id=report.id,
        target_session_date=target_date,
        status=evaluation_status,
        attempt_count=1,
        evaluated_count=sum(value is not None for value in values),
        pending_count=sum(value is None for value in values),
        failed_count=0,
        started_at=datetime(2026, 7, 21, 15, 0, tzinfo=UTC),
        completed_at=(
            datetime(2026, 7, 21, 15, 5, tzinfo=UTC)
            if evaluation_status == "complete"
            else None
        ),
        last_attempt_at=datetime(2026, 7, 21, 15, 0, tzinfo=UTC),
        details={"negative_results_retained": True},
    )
    db.add(evaluation)
    db.flush()
    outcomes: list[MarketReportItemOutcome] = []
    for index, return_bp in enumerate(values, start=1):
        ticker = f"S{target_date.day:02d}{index}"
        item = MarketReportItem(
            report_id=report.id,
            ticker=ticker,
            rank=index,
            score_bp=8000 - index,
            payload={
                "price_at_analysis": 100.0,
                "expected_direction": "up",
                "analysis": {
                    "targets": [105.0, 110.0],
                    "stop_loss": 95.0,
                },
            },
        )
        db.add(item)
        db.flush()
        complete = return_bp is not None
        close = None if return_bp is None else Decimal("100") * (
            Decimal("1") + Decimal(return_bp) / Decimal("10000")
        )
        outcome = MarketReportItemOutcome(
            evaluation_id=evaluation.id,
            report_id=report.id,
            report_item_id=item.id,
            ticker=ticker,
            rank=index,
            target_session_date=target_date,
            status="complete" if complete else "pending_data",
            expected_direction="up",
            price_at_analysis=Decimal("100"),
            session_open=Decimal("100") if complete else None,
            session_high=(max(Decimal("106"), close) if complete and close else None),
            session_low=Decimal("94") if complete else None,
            session_close=close,
            return_bp=return_bp,
            max_upside_bp=600 if complete else None,
            max_drawdown_bp=-600 if complete else None,
            direction_correct=None if return_bp is None else return_bp > 0,
            target_one=Decimal("105"),
            target_two=Decimal("110"),
            stop_loss=Decimal("95"),
            target_one_hit=True if complete else None,
            target_two_hit=False if complete else None,
            stop_loss_hit=True if complete else None,
            provider="fixture" if complete else None,
            data_fingerprint=f"fp-{ticker}" if complete else None,
            data_as_of=(
                datetime.combine(target_date, datetime.min.time(), tzinfo=UTC)
                if complete
                else None
            ),
            evaluated_at=(datetime(2026, 7, 21, 15, 5, tzinfo=UTC) if complete else None),
            evaluator_version="report-performance-v1",
            evidence=(
                {"negative_results_retained": True}
                if complete
                else {"reason": "target_session_candle_missing", "retryable": True}
            ),
        )
        db.add(outcome)
        outcomes.append(outcome)
    db.commit()
    return report, outcomes


def test_summary_keeps_negative_results_and_reports_completeness(
    db_session: Session,
) -> None:
    _create_report(
        db_session,
        target_date=date(2026, 7, 20),
        values=[100, -200],
        evaluation_status="complete",
    )
    _create_report(
        db_session,
        target_date=date(2026, 7, 21),
        values=[300, 0],
        evaluation_status="complete",
    )
    _create_report(
        db_session,
        target_date=date(2026, 7, 22),
        values=[-100, None],
        evaluation_status="partial",
    )

    summary = get_performance_summary(
        db_session,
        window_sessions=7,
        moment=_moment(),
    )

    assert summary["sessions_found"] == 3
    assert summary["complete_sessions"] == 2
    assert summary["total_items"] == 6
    assert summary["evaluated_items"] == 5
    assert summary["positive_count"] == 2
    assert summary["negative_count"] == 2
    assert summary["flat_count"] == 1
    assert summary["data_completeness_pct"] == 83.33
    assert summary["best_outcome"]["return_bp"] == 300
    assert summary["worst_outcome"]["return_bp"] == -200
    assert summary["negative_results_retained"] is True
    assert len(summary["ranks"]) == 10


def test_report_history_detail_delayed_and_csv_are_transparent(
    db_session: Session,
) -> None:
    complete_report, _ = _create_report(
        db_session,
        target_date=date(2026, 7, 20),
        values=[100, -200],
        evaluation_status="complete",
    )
    delayed_report, _ = _create_report(
        db_session,
        target_date=date(2026, 7, 21),
        values=[-100, None],
        evaluation_status="partial",
    )

    history, total = list_performance_reports(
        db_session,
        limit=10,
        offset=0,
        moment=_moment(),
    )
    detail = get_performance_report_detail(
        db_session,
        report_id=complete_report.id,
        moment=_moment(),
    )
    delayed, delayed_total = list_delayed_performance_reports(
        db_session,
        moment=_moment(),
    )
    csv_text = export_performance_csv(
        db_session,
        window_sessions=7,
        moment=_moment(),
    )

    assert total == 2
    assert history[0]["report_id"] == delayed_report.id
    assert any(item["return_bp"] == -200 for item in detail["outcomes"])
    assert delayed_total == 1
    assert delayed[0]["report_id"] == delayed_report.id
    assert "target_session_candle_missing" in delayed[0]["reasons"]
    assert "-200" in csv_text
    assert "pending_data" in csv_text


def test_admin_correction_creates_revision_and_completes_evaluation(
    db_session: Session,
) -> None:
    report, outcomes = _create_report(
        db_session,
        target_date=date(2026, 7, 21),
        values=[-100, None],
        evaluation_status="partial",
    )
    admin = User(
        email="performance-admin@example.com",
        password_hash="hashed-password",
        display_name="Performance Admin",
        avatar_key="avatar_01",
        status="active",
        email_verified=True,
    )
    db_session.add(admin)
    db_session.commit()

    corrected, revision = correct_performance_outcome(
        db_session,
        outcome_id=outcomes[1].id,
        actor_user_id=admin.id,
        reason="Provider corrected the official session candle.",
        session_open=100.0,
        session_high=112.0,
        session_low=98.0,
        session_close=110.0,
        provider="official-correction",
        data_fingerprint="corrected-fingerprint",
        data_as_of=datetime(2026, 7, 21, 15, 0, tzinfo=UTC),
    )

    assert corrected.status == "complete"
    assert corrected.return_bp == 1000
    assert revision.revision_number == 1
    assert revision.before_payload["status"] == "pending_data"
    assert revision.after_payload["status"] == "complete"
    evaluation = db_session.scalar(
        select(MarketReportEvaluation).where(
            MarketReportEvaluation.report_id == report.id
        )
    )
    assert evaluation is not None
    assert evaluation.status == "complete"
    assert evaluation.evaluated_count == 2
    assert db_session.scalar(select(func.count(MarketReportOutcomeRevision.id))) == 1
    event = db_session.scalar(
        select(CommunityAdminEvent).where(
            CommunityAdminEvent.action == "report_outcome_corrected"
        )
    )
    assert event is not None
    assert event.details["revision_number"] == 1
