from __future__ import annotations

import csv
import io
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from statistics import mean, median
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.market_calendar import EGXTradingCalendar
from app.models import (
    CommunityAdminEvent,
    MarketReport,
    MarketReportEvaluation,
    MarketReportItem,
    MarketReportItemOutcome,
    MarketReportOutcomeRevision,
)
from app.services.report_performance import (
    EVALUATOR_VERSION,
    _basis_points,
    _direction_correct,
    _level_hit,
    _stop_hit,
)

CORRECTED_EVALUATOR_VERSION = "report-performance-v1-corrected"


class PerformanceExperienceError(RuntimeError):
    """Base error for transparent report-performance views."""


class PerformanceReportNotFoundError(PerformanceExperienceError):
    """Raised when a report or outcome cannot be found."""


class PerformanceCorrectionError(PerformanceExperienceError):
    """Raised when an administrator correction is invalid."""


@dataclass(frozen=True, slots=True)
class PerformanceContext:
    reports: tuple[MarketReport, ...]
    item_counts: dict[UUID, int]
    evaluations: dict[UUID, MarketReportEvaluation]
    outcomes: dict[UUID, tuple[MarketReportItemOutcome, ...]]
    correction_counts: dict[UUID, int]


def _aware(moment: datetime | None) -> datetime:
    current = moment or datetime.now(UTC)
    return current if current.tzinfo is not None else current.replace(tzinfo=UTC)


def _is_due(
    target_session_date: date,
    *,
    moment: datetime,
    calendar: EGXTradingCalendar,
) -> bool:
    local = moment.astimezone(calendar.timezone)
    if target_session_date < local.date():
        return True
    if target_session_date > local.date():
        return False
    return local.timetz().replace(tzinfo=None) >= calendar.scan_time


def _percent(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator * 100 / denominator, 2)


def _mean_bp(values: list[int]) -> int | None:
    return int(round(mean(values))) if values else None


def _median_bp(values: list[int]) -> int | None:
    return int(round(median(values))) if values else None


def _float(value: Decimal | None) -> float | None:
    return None if value is None else float(value)


def _due_reports(
    db: Session,
    *,
    moment: datetime | None = None,
    maximum: int = 500,
) -> tuple[MarketReport, ...]:
    current = _aware(moment)
    calendar = EGXTradingCalendar.from_settings()
    candidates = db.scalars(
        select(MarketReport)
        .where(MarketReport.status == "complete")
        .order_by(MarketReport.target_session_date.desc(), MarketReport.id.desc())
        .limit(maximum * 2)
    ).all()
    due = [
        report
        for report in candidates
        if _is_due(report.target_session_date, moment=current, calendar=calendar)
    ]
    return tuple(due[:maximum])


def _load_context(
    db: Session,
    reports: tuple[MarketReport, ...],
) -> PerformanceContext:
    report_ids = [report.id for report in reports]
    if not report_ids:
        return PerformanceContext((), {}, {}, {}, {})

    item_counts = {
        report_id: int(count)
        for report_id, count in db.execute(
            select(MarketReportItem.report_id, func.count(MarketReportItem.id))
            .where(MarketReportItem.report_id.in_(report_ids))
            .group_by(MarketReportItem.report_id)
        ).all()
    }
    evaluations = {
        item.report_id: item
        for item in db.scalars(
            select(MarketReportEvaluation).where(MarketReportEvaluation.report_id.in_(report_ids))
        ).all()
    }
    grouped_outcomes: dict[UUID, list[MarketReportItemOutcome]] = defaultdict(list)
    outcome_rows = db.scalars(
        select(MarketReportItemOutcome)
        .where(MarketReportItemOutcome.report_id.in_(report_ids))
        .order_by(
            MarketReportItemOutcome.target_session_date.desc(),
            MarketReportItemOutcome.rank,
        )
    ).all()
    for outcome in outcome_rows:
        grouped_outcomes[outcome.report_id].append(outcome)

    outcome_ids = [item.id for item in outcome_rows]
    correction_counts: dict[UUID, int] = {}
    if outcome_ids:
        correction_counts = {
            outcome_id: int(count)
            for outcome_id, count in db.execute(
                select(
                    MarketReportOutcomeRevision.outcome_id,
                    func.count(MarketReportOutcomeRevision.id),
                )
                .where(MarketReportOutcomeRevision.outcome_id.in_(outcome_ids))
                .group_by(MarketReportOutcomeRevision.outcome_id)
            ).all()
        }
    return PerformanceContext(
        reports=reports,
        item_counts=item_counts,
        evaluations=evaluations,
        outcomes={key: tuple(value) for key, value in grouped_outcomes.items()},
        correction_counts=correction_counts,
    )


def _evaluation_status(
    evaluation: MarketReportEvaluation | None,
    *,
    total_items: int,
) -> str:
    if evaluation is None:
        return "not_started" if total_items > 0 else "empty_report"
    return evaluation.status


def _completed(outcomes: tuple[MarketReportItemOutcome, ...]) -> list[MarketReportItemOutcome]:
    return [item for item in outcomes if item.status == "complete" and item.return_bp is not None]


def _session_payload(
    report: MarketReport,
    *,
    total_items: int,
    evaluation: MarketReportEvaluation | None,
    outcomes: tuple[MarketReportItemOutcome, ...],
) -> dict:
    completed = _completed(outcomes)
    returns = [item.return_bp for item in completed if item.return_bp is not None]
    positive_count = sum(value > 0 for value in returns)
    negative_count = sum(value < 0 for value in returns)
    direction_values = [item.direction_correct for item in completed if item.direction_correct is not None]
    target_one_values = [item.target_one_hit for item in completed if item.target_one_hit is not None]
    stop_values = [item.stop_loss_hit for item in completed if item.stop_loss_hit is not None]
    pending_items = sum(item.status == "pending_data" for item in outcomes)
    failed_items = sum(item.status == "failed" for item in outcomes)
    return {
        "report_id": report.id,
        "target_session_date": report.target_session_date,
        "evaluation_status": _evaluation_status(evaluation, total_items=total_items),
        "total_items": total_items,
        "evaluated_items": len(completed),
        "pending_items": pending_items,
        "failed_items": failed_items,
        "data_completeness_pct": _percent(len(completed), total_items) or 0.0,
        "average_return_bp": _mean_bp(returns),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "direction_accuracy_pct": _percent(sum(direction_values), len(direction_values)),
        "target_one_hit_rate_pct": _percent(
            sum(target_one_values),
            len(target_one_values),
        ),
        "stop_loss_hit_rate_pct": _percent(sum(stop_values), len(stop_values)),
    }


def _best_worst_payload(outcome: MarketReportItemOutcome) -> dict:
    if outcome.return_bp is None:
        raise PerformanceExperienceError("Completed outcome has no return")
    return {
        "report_id": outcome.report_id,
        "target_session_date": outcome.target_session_date,
        "ticker": outcome.ticker,
        "rank": outcome.rank,
        "return_bp": outcome.return_bp,
    }


def _rank_payload(
    rank: int,
    outcomes: list[MarketReportItemOutcome],
) -> dict:
    completed = _completed(tuple(outcomes))
    returns = [item.return_bp for item in completed if item.return_bp is not None]
    direction_values = [item.direction_correct for item in completed if item.direction_correct is not None]
    target_values = [item.target_one_hit for item in completed if item.target_one_hit is not None]
    stop_values = [item.stop_loss_hit for item in completed if item.stop_loss_hit is not None]
    return {
        "rank": rank,
        "evaluated_items": len(completed),
        "average_return_bp": _mean_bp(returns),
        "median_return_bp": _median_bp(returns),
        "positive_rate_pct": _percent(sum(value > 0 for value in returns), len(returns)),
        "direction_accuracy_pct": _percent(sum(direction_values), len(direction_values)),
        "target_one_hit_rate_pct": _percent(sum(target_values), len(target_values)),
        "stop_loss_hit_rate_pct": _percent(sum(stop_values), len(stop_values)),
    }


def get_performance_summary(
    db: Session,
    *,
    window_sessions: int,
    moment: datetime | None = None,
) -> dict:
    if window_sessions not in {7, 30}:
        raise PerformanceExperienceError("Performance window must be 7 or 30 sessions")
    reports = _due_reports(db, moment=moment, maximum=window_sessions)
    context = _load_context(db, reports)
    all_outcomes = [outcome for report in reports for outcome in context.outcomes.get(report.id, ())]
    completed = _completed(tuple(all_outcomes))
    returns = [item.return_bp for item in completed if item.return_bp is not None]
    direction_values = [item.direction_correct for item in completed if item.direction_correct is not None]
    target_one_values = [item.target_one_hit for item in completed if item.target_one_hit is not None]
    target_two_values = [item.target_two_hit for item in completed if item.target_two_hit is not None]
    stop_values = [item.stop_loss_hit for item in completed if item.stop_loss_hit is not None]
    total_items = sum(context.item_counts.get(report.id, 0) for report in reports)
    pending_items = sum(item.status == "pending_data" for item in all_outcomes)
    failed_items = sum(item.status == "failed" for item in all_outcomes)
    rank_groups: dict[int, list[MarketReportItemOutcome]] = defaultdict(list)
    for outcome in all_outcomes:
        rank_groups[outcome.rank].append(outcome)
    sessions = [
        _session_payload(
            report,
            total_items=context.item_counts.get(report.id, 0),
            evaluation=context.evaluations.get(report.id),
            outcomes=context.outcomes.get(report.id, ()),
        )
        for report in reports
    ]
    best = max(completed, key=lambda item: item.return_bp or 0, default=None)
    worst = min(completed, key=lambda item: item.return_bp or 0, default=None)
    return {
        "window_sessions": window_sessions,
        "sessions_found": len(reports),
        "complete_sessions": sum(
            context.evaluations.get(report.id) is not None
            and context.evaluations[report.id].status == "complete"
            for report in reports
        ),
        "total_items": total_items,
        "evaluated_items": len(completed),
        "pending_items": pending_items,
        "failed_items": failed_items,
        "data_completeness_pct": _percent(len(completed), total_items) or 0.0,
        "positive_count": sum(value > 0 for value in returns),
        "negative_count": sum(value < 0 for value in returns),
        "flat_count": sum(value == 0 for value in returns),
        "average_return_bp": _mean_bp(returns),
        "median_return_bp": _median_bp(returns),
        "positive_rate_pct": _percent(sum(value > 0 for value in returns), len(returns)),
        "direction_accuracy_pct": _percent(sum(direction_values), len(direction_values)),
        "target_one_hit_rate_pct": _percent(
            sum(target_one_values),
            len(target_one_values),
        ),
        "target_two_hit_rate_pct": _percent(
            sum(target_two_values),
            len(target_two_values),
        ),
        "stop_loss_hit_rate_pct": _percent(sum(stop_values), len(stop_values)),
        "best_outcome": None if best is None else _best_worst_payload(best),
        "worst_outcome": None if worst is None else _best_worst_payload(worst),
        "ranks": [_rank_payload(rank, rank_groups[rank]) for rank in range(1, 11)],
        "sessions": sessions,
        "benchmark": {
            "status": "not_available",
            "symbol": "EGX30",
            "reason": "Benchmark session ledger is not implemented yet.",
        },
        "negative_results_retained": True,
    }


def list_performance_reports(
    db: Session,
    *,
    limit: int = 30,
    offset: int = 0,
    moment: datetime | None = None,
) -> tuple[list[dict], int]:
    reports = _due_reports(db, moment=moment, maximum=500)
    total = len(reports)
    selected = tuple(reports[offset : offset + limit])
    context = _load_context(db, selected)
    items: list[dict] = []
    for report in selected:
        session = _session_payload(
            report,
            total_items=context.item_counts.get(report.id, 0),
            evaluation=context.evaluations.get(report.id),
            outcomes=context.outcomes.get(report.id, ()),
        )
        items.append(
            {
                "report_id": report.id,
                "target_session_date": report.target_session_date,
                "generated_at": report.generated_at,
                **{key: value for key, value in session.items() if key != "report_id"},
            }
        )
    return items, total


def _outcome_payload(
    outcome: MarketReportItemOutcome,
    *,
    correction_count: int,
) -> dict:
    return {
        "id": outcome.id,
        "ticker": outcome.ticker,
        "rank": outcome.rank,
        "status": outcome.status,
        "expected_direction": outcome.expected_direction,
        "price_at_analysis": float(outcome.price_at_analysis),
        "session_open": _float(outcome.session_open),
        "session_high": _float(outcome.session_high),
        "session_low": _float(outcome.session_low),
        "session_close": _float(outcome.session_close),
        "return_bp": outcome.return_bp,
        "max_upside_bp": outcome.max_upside_bp,
        "max_drawdown_bp": outcome.max_drawdown_bp,
        "direction_correct": outcome.direction_correct,
        "target_one": _float(outcome.target_one),
        "target_two": _float(outcome.target_two),
        "stop_loss": _float(outcome.stop_loss),
        "target_one_hit": outcome.target_one_hit,
        "target_two_hit": outcome.target_two_hit,
        "stop_loss_hit": outcome.stop_loss_hit,
        "provider": outcome.provider,
        "data_as_of": outcome.data_as_of,
        "evaluated_at": outcome.evaluated_at,
        "evaluator_version": outcome.evaluator_version,
        "evidence": outcome.evidence,
        "correction_count": correction_count,
    }


def _revision_payload(revision: MarketReportOutcomeRevision) -> dict:
    return {
        "id": revision.id,
        "revision_number": revision.revision_number,
        "reason": revision.reason,
        "before_payload": revision.before_payload,
        "after_payload": revision.after_payload,
        "created_at": revision.created_at,
    }


def get_performance_report_detail(
    db: Session,
    *,
    report_id: UUID,
    moment: datetime | None = None,
) -> dict:
    report = db.scalar(
        select(MarketReport).where(
            MarketReport.id == report_id,
            MarketReport.status == "complete",
        )
    )
    if report is None:
        raise PerformanceReportNotFoundError("Performance report was not found")
    calendar = EGXTradingCalendar.from_settings()
    if not _is_due(report.target_session_date, moment=_aware(moment), calendar=calendar):
        raise PerformanceReportNotFoundError("Performance is not available before close")
    context = _load_context(db, (report,))
    outcomes = context.outcomes.get(report.id, ())
    revisions = db.scalars(
        select(MarketReportOutcomeRevision)
        .where(MarketReportOutcomeRevision.report_id == report.id)
        .order_by(
            MarketReportOutcomeRevision.created_at,
            MarketReportOutcomeRevision.revision_number,
        )
    ).all()
    return {
        "report_id": report.id,
        "target_session_date": report.target_session_date,
        "generated_at": report.generated_at,
        "evaluation_status": _evaluation_status(
            context.evaluations.get(report.id),
            total_items=context.item_counts.get(report.id, 0),
        ),
        "session": _session_payload(
            report,
            total_items=context.item_counts.get(report.id, 0),
            evaluation=context.evaluations.get(report.id),
            outcomes=outcomes,
        ),
        "outcomes": [
            _outcome_payload(
                outcome,
                correction_count=context.correction_counts.get(outcome.id, 0),
            )
            for outcome in outcomes
        ],
        "revisions": [_revision_payload(item) for item in revisions],
        "negative_results_retained": True,
    }


def list_delayed_performance_reports(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
    moment: datetime | None = None,
) -> tuple[list[dict], int]:
    reports = _due_reports(db, moment=moment, maximum=500)
    context = _load_context(db, reports)
    delayed: list[dict] = []
    for report in reports:
        total_items = context.item_counts.get(report.id, 0)
        evaluation = context.evaluations.get(report.id)
        outcomes = context.outcomes.get(report.id, ())
        completed_count = len(_completed(outcomes))
        if total_items > 0 and completed_count == total_items:
            continue
        reasons = sorted(
            {str(item.evidence.get("reason", "unknown")) for item in outcomes if item.status != "complete"}
        )
        if evaluation is None:
            reasons.append("evaluation_not_started")
        delayed.append(
            {
                "report_id": report.id,
                "target_session_date": report.target_session_date,
                "evaluation_id": None if evaluation is None else evaluation.id,
                "evaluation_status": _evaluation_status(
                    evaluation,
                    total_items=total_items,
                ),
                "total_items": total_items,
                "evaluated_items": completed_count,
                "pending_items": sum(item.status == "pending_data" for item in outcomes),
                "failed_items": sum(item.status == "failed" for item in outcomes),
                "last_attempt_at": None if evaluation is None else evaluation.last_attempt_at,
                "reasons": reasons,
            }
        )
    total = len(delayed)
    return delayed[offset : offset + limit], total


def export_performance_csv(
    db: Session,
    *,
    window_sessions: int,
    moment: datetime | None = None,
) -> str:
    if window_sessions not in {7, 30}:
        raise PerformanceExperienceError("Performance window must be 7 or 30 sessions")
    reports = _due_reports(db, moment=moment, maximum=window_sessions)
    context = _load_context(db, reports)
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "report_id",
            "target_session_date",
            "ticker",
            "rank",
            "status",
            "price_at_analysis",
            "session_open",
            "session_high",
            "session_low",
            "session_close",
            "return_bp",
            "max_upside_bp",
            "max_drawdown_bp",
            "direction_correct",
            "target_one_hit",
            "target_two_hit",
            "stop_loss_hit",
            "provider",
            "data_as_of",
            "evaluator_version",
            "correction_count",
        ]
    )
    for report in reports:
        for outcome in context.outcomes.get(report.id, ()):
            writer.writerow(
                [
                    report.id,
                    report.target_session_date.isoformat(),
                    outcome.ticker,
                    outcome.rank,
                    outcome.status,
                    outcome.price_at_analysis,
                    outcome.session_open,
                    outcome.session_high,
                    outcome.session_low,
                    outcome.session_close,
                    outcome.return_bp,
                    outcome.max_upside_bp,
                    outcome.max_drawdown_bp,
                    outcome.direction_correct,
                    outcome.target_one_hit,
                    outcome.target_two_hit,
                    outcome.stop_loss_hit,
                    outcome.provider,
                    None if outcome.data_as_of is None else outcome.data_as_of.isoformat(),
                    outcome.evaluator_version,
                    context.correction_counts.get(outcome.id, 0),
                ]
            )
    return output.getvalue()


def _snapshot(outcome: MarketReportItemOutcome) -> dict:
    return {
        "status": outcome.status,
        "session_open": _float(outcome.session_open),
        "session_high": _float(outcome.session_high),
        "session_low": _float(outcome.session_low),
        "session_close": _float(outcome.session_close),
        "return_bp": outcome.return_bp,
        "max_upside_bp": outcome.max_upside_bp,
        "max_drawdown_bp": outcome.max_drawdown_bp,
        "direction_correct": outcome.direction_correct,
        "target_one_hit": outcome.target_one_hit,
        "target_two_hit": outcome.target_two_hit,
        "stop_loss_hit": outcome.stop_loss_hit,
        "provider": outcome.provider,
        "data_fingerprint": outcome.data_fingerprint,
        "data_as_of": None if outcome.data_as_of is None else outcome.data_as_of.isoformat(),
        "evaluated_at": None if outcome.evaluated_at is None else outcome.evaluated_at.isoformat(),
        "evaluator_version": outcome.evaluator_version,
        "evidence": outcome.evidence,
    }


def _refresh_evaluation(db: Session, outcome: MarketReportItemOutcome, moment: datetime) -> None:
    evaluation = db.scalar(
        select(MarketReportEvaluation)
        .where(MarketReportEvaluation.id == outcome.evaluation_id)
        .with_for_update()
    )
    if evaluation is None:
        raise PerformanceCorrectionError("Outcome evaluation is missing")
    total_items = int(
        db.scalar(
            select(func.count(MarketReportItem.id)).where(MarketReportItem.report_id == outcome.report_id)
        )
        or 0
    )
    statuses = db.execute(
        select(
            MarketReportItemOutcome.status,
            func.count(MarketReportItemOutcome.id),
        )
        .where(MarketReportItemOutcome.report_id == outcome.report_id)
        .group_by(MarketReportItemOutcome.status)
    ).all()
    counts = {status: int(count) for status, count in statuses}
    evaluation.evaluated_count = counts.get("complete", 0)
    evaluation.pending_count = counts.get("pending_data", 0)
    evaluation.failed_count = counts.get("failed", 0)
    if total_items > 0 and evaluation.evaluated_count == total_items:
        evaluation.status = "complete"
        evaluation.completed_at = moment
    elif total_items > 0 and evaluation.failed_count == total_items:
        evaluation.status = "failed"
        evaluation.completed_at = moment
    else:
        evaluation.status = "partial"
        evaluation.completed_at = None
    evaluation.details = {
        **evaluation.details,
        "item_count": total_items,
        "evaluated_count": evaluation.evaluated_count,
        "pending_count": evaluation.pending_count,
        "failed_count": evaluation.failed_count,
        "latest_admin_correction_at": moment.isoformat(),
        "negative_results_retained": True,
    }


def correct_performance_outcome(
    db: Session,
    *,
    outcome_id: UUID,
    actor_user_id: UUID,
    reason: str,
    session_open: float,
    session_high: float,
    session_low: float,
    session_close: float,
    provider: str,
    data_fingerprint: str,
    data_as_of: datetime,
) -> tuple[MarketReportItemOutcome, MarketReportOutcomeRevision]:
    outcome = db.scalar(
        select(MarketReportItemOutcome).where(MarketReportItemOutcome.id == outcome_id).with_for_update()
    )
    if outcome is None:
        raise PerformanceReportNotFoundError("Performance outcome was not found")
    values = {
        "open": Decimal(str(session_open)),
        "high": Decimal(str(session_high)),
        "low": Decimal(str(session_low)),
        "close": Decimal(str(session_close)),
    }
    if values["low"] > values["high"]:
        raise PerformanceCorrectionError("Session low cannot exceed session high")
    if values["open"] < values["low"] or values["open"] > values["high"]:
        raise PerformanceCorrectionError("Session open must be inside the high/low range")
    if values["close"] < values["low"] or values["close"] > values["high"]:
        raise PerformanceCorrectionError("Session close must be inside the high/low range")

    before = _snapshot(outcome)
    moment = datetime.now(UTC)
    outcome.status = "complete"
    outcome.session_open = values["open"]
    outcome.session_high = values["high"]
    outcome.session_low = values["low"]
    outcome.session_close = values["close"]
    outcome.return_bp = _basis_points(values["close"], outcome.price_at_analysis)
    outcome.max_upside_bp = _basis_points(values["high"], outcome.price_at_analysis)
    outcome.max_drawdown_bp = _basis_points(values["low"], outcome.price_at_analysis)
    outcome.direction_correct = _direction_correct(
        outcome.expected_direction,
        outcome.return_bp,
    )
    outcome.target_one_hit = _level_hit(
        outcome.target_one,
        expected_direction=outcome.expected_direction,
        session_high=values["high"],
        session_low=values["low"],
    )
    outcome.target_two_hit = _level_hit(
        outcome.target_two,
        expected_direction=outcome.expected_direction,
        session_high=values["high"],
        session_low=values["low"],
    )
    outcome.stop_loss_hit = _stop_hit(
        outcome.stop_loss,
        expected_direction=outcome.expected_direction,
        session_high=values["high"],
        session_low=values["low"],
    )
    outcome.provider = provider.strip()
    outcome.data_fingerprint = data_fingerprint.strip()
    outcome.data_as_of = _aware(data_as_of)
    outcome.evaluated_at = moment
    outcome.evaluator_version = CORRECTED_EVALUATOR_VERSION
    outcome.evidence = {
        **outcome.evidence,
        "admin_corrected": True,
        "correction_reason": reason.strip(),
        "corrected_at": moment.isoformat(),
        "original_evaluator_version": EVALUATOR_VERSION,
        "negative_results_retained": True,
    }
    revision_number = (
        int(
            db.scalar(
                select(func.max(MarketReportOutcomeRevision.revision_number)).where(
                    MarketReportOutcomeRevision.outcome_id == outcome.id
                )
            )
            or 0
        )
        + 1
    )
    after = _snapshot(outcome)
    revision = MarketReportOutcomeRevision(
        outcome_id=outcome.id,
        report_id=outcome.report_id,
        actor_user_id=actor_user_id,
        revision_number=revision_number,
        reason=reason.strip(),
        before_payload=before,
        after_payload=after,
    )
    db.add(revision)
    db.flush()
    _refresh_evaluation(db, outcome, moment)
    db.add(
        CommunityAdminEvent(
            actor_user_id=actor_user_id,
            action="report_outcome_corrected",
            reason_code="market_data_correction",
            details={
                "outcome_id": str(outcome.id),
                "report_id": str(outcome.report_id),
                "ticker": outcome.ticker,
                "revision_id": str(revision.id),
                "revision_number": revision.revision_number,
                "reason": revision.reason,
            },
        )
    )
    db.commit()
    return outcome, revision


def performance_outcome_response(
    db: Session,
    outcome: MarketReportItemOutcome,
) -> dict:
    count = int(
        db.scalar(
            select(func.count(MarketReportOutcomeRevision.id)).where(
                MarketReportOutcomeRevision.outcome_id == outcome.id
            )
        )
        or 0
    )
    return _outcome_payload(outcome, correction_count=count)


def performance_revision_response(revision: MarketReportOutcomeRevision) -> dict:
    return _revision_payload(revision)
