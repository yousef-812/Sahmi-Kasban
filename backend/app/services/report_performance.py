from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_calendar import EGXTradingCalendar
from app.market_data.types import CandleSeries, MarketDataProvider
from app.models import (
    MarketReport,
    MarketReportEvaluation,
    MarketReportItem,
    MarketReportItemOutcome,
)

EVALUATOR_VERSION = "report-performance-v1"
_RUNNING_TTL = timedelta(hours=2)


class ReportPerformanceError(RuntimeError):
    """Base error for the daily report performance ledger."""


class ReportEvaluationNotFoundError(ReportPerformanceError):
    """Raised when a complete report cannot be found."""


class ReportEvaluationNotDueError(ReportPerformanceError):
    """Raised when the target EGX session has not closed yet."""


class ReportEvaluationAlreadyRunningError(ReportPerformanceError):
    """Raised when another worker owns a recent evaluation attempt."""


@dataclass(frozen=True, slots=True)
class ReportEvaluationResult:
    evaluation: MarketReportEvaluation
    outcomes: tuple[MarketReportItemOutcome, ...]
    idempotent: bool


@dataclass(frozen=True, slots=True)
class DueReportEvaluationResult:
    scanned_reports: int
    completed_reports: int
    partial_reports: int
    failed_reports: int
    skipped_reports: int
    evaluation_ids: tuple[UUID, ...]


def _aware(moment: datetime | None) -> datetime:
    current = moment or datetime.now(UTC)
    if current.tzinfo is None:
        return current.replace(tzinfo=UTC)
    return current


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


def _decimal(value: object) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not result.is_finite() or result <= 0:
        return None
    return result


def _basis_points(value: Decimal, reference: Decimal) -> int:
    return int(round(float((value / reference - Decimal("1")) * Decimal("10000"))))


def _parse_timestamp(value: object, *, calendar: EGXTradingCalendar) -> datetime | None:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, datetime.min.time(), tzinfo=calendar.timezone)
    elif isinstance(value, str):
        normalized = value.strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
    else:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=calendar.timezone)
    return parsed


def _session_candle(
    series: CandleSeries,
    *,
    target_session_date: date,
    calendar: EGXTradingCalendar,
) -> dict[str, object] | None:
    matches: list[tuple[datetime, dict[str, object]]] = []
    for raw in series.candles:
        timestamp = _parse_timestamp(raw.get("timestamp"), calendar=calendar)
        if timestamp is None:
            continue
        if timestamp.astimezone(calendar.timezone).date() == target_session_date:
            matches.append((timestamp, raw))
    if not matches:
        return None
    matches.sort(key=lambda item: item[0])
    return matches[-1][1]


def _prediction_levels(payload: dict[str, Any]) -> tuple[Decimal | None, Decimal | None, Decimal | None]:
    analysis = payload.get("analysis")
    if not isinstance(analysis, dict):
        analysis = {}
    targets = analysis.get("targets")
    if not isinstance(targets, list):
        targets = []
    target_one = _decimal(targets[0]) if len(targets) >= 1 else None
    target_two = _decimal(targets[1]) if len(targets) >= 2 else None
    stop_loss = _decimal(analysis.get("stop_loss"))
    return target_one, target_two, stop_loss


def _direction_correct(expected_direction: str, return_bp: int) -> bool:
    if expected_direction == "down":
        return return_bp < 0
    if expected_direction == "neutral":
        return abs(return_bp) <= 50
    return return_bp > 0


def _level_hit(
    level: Decimal | None,
    *,
    expected_direction: str,
    session_high: Decimal,
    session_low: Decimal,
) -> bool | None:
    if level is None:
        return None
    if expected_direction == "down":
        return session_low <= level
    return session_high >= level


def _stop_hit(
    stop_loss: Decimal | None,
    *,
    expected_direction: str,
    session_high: Decimal,
    session_low: Decimal,
) -> bool | None:
    if stop_loss is None:
        return None
    if expected_direction == "down":
        return session_high >= stop_loss
    return session_low <= stop_loss


def _outcomes_for_evaluation(
    db: Session,
    evaluation_id: UUID,
) -> tuple[MarketReportItemOutcome, ...]:
    return tuple(
        db.scalars(
            select(MarketReportItemOutcome)
            .where(MarketReportItemOutcome.evaluation_id == evaluation_id)
            .order_by(MarketReportItemOutcome.rank)
        ).all()
    )


def _get_complete_report(db: Session, report_id: UUID) -> MarketReport:
    report = db.scalar(
        select(MarketReport).where(
            MarketReport.id == report_id,
            MarketReport.status == "complete",
        )
    )
    if report is None:
        raise ReportEvaluationNotFoundError("Complete market report was not found")
    return report


def _start_evaluation(
    db: Session,
    *,
    report: MarketReport,
    moment: datetime,
) -> tuple[MarketReportEvaluation, bool]:
    evaluation = db.scalar(
        select(MarketReportEvaluation)
        .where(MarketReportEvaluation.report_id == report.id)
        .with_for_update()
    )
    if evaluation is not None and evaluation.status == "complete":
        return evaluation, True
    if (
        evaluation is not None
        and evaluation.status == "running"
        and evaluation.last_attempt_at is not None
        and evaluation.last_attempt_at > moment - _RUNNING_TTL
    ):
        raise ReportEvaluationAlreadyRunningError("Report evaluation is already running")

    if evaluation is None:
        evaluation = MarketReportEvaluation(
            report_id=report.id,
            target_session_date=report.target_session_date,
            status="running",
            attempt_count=1,
            evaluated_count=0,
            pending_count=0,
            failed_count=0,
            started_at=moment,
            completed_at=None,
            last_attempt_at=moment,
            details={"evaluator_version": EVALUATOR_VERSION},
        )
        db.add(evaluation)
    else:
        evaluation.status = "running"
        evaluation.attempt_count += 1
        evaluation.started_at = moment
        evaluation.completed_at = None
        evaluation.last_attempt_at = moment
        evaluation.details = {
            **evaluation.details,
            "evaluator_version": EVALUATOR_VERSION,
        }
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raced = db.scalar(
            select(MarketReportEvaluation).where(
                MarketReportEvaluation.report_id == report.id
            )
        )
        if raced is None:
            raise
        if raced.status == "complete":
            return raced, True
        raise ReportEvaluationAlreadyRunningError(
            "Report evaluation was started concurrently"
        ) from exc
    return evaluation, False


async def _fetch_series(
    provider: MarketDataProvider,
    ticker: str,
    *,
    semaphore: asyncio.Semaphore,
) -> CandleSeries:
    settings = get_settings()
    async with semaphore:
        return await provider.get_history(
            ticker,
            period=settings.market_data_period,
            interval=settings.market_data_interval,
        )


def _base_outcome(
    item: MarketReportItem,
    *,
    evaluation: MarketReportEvaluation,
    price_at_analysis: Decimal,
    expected_direction: str,
) -> MarketReportItemOutcome:
    existing = None
    return MarketReportItemOutcome(
        evaluation_id=evaluation.id,
        report_id=item.report_id,
        report_item_id=item.id,
        ticker=item.ticker,
        rank=item.rank,
        target_session_date=evaluation.target_session_date,
        status="pending_data",
        expected_direction=expected_direction,
        price_at_analysis=price_at_analysis,
        evaluator_version=EVALUATOR_VERSION,
        evidence={},
    )


def _apply_pending(
    outcome: MarketReportItemOutcome,
    *,
    reason: str,
    details: dict[str, object] | None = None,
) -> None:
    if outcome.status == "complete":
        return
    outcome.status = "pending_data"
    outcome.evaluated_at = None
    outcome.evidence = {
        "reason": reason,
        "retryable": True,
        "evaluator_version": EVALUATOR_VERSION,
        **(details or {}),
    }


def _apply_failed(
    outcome: MarketReportItemOutcome,
    *,
    reason: str,
    details: dict[str, object] | None = None,
) -> None:
    if outcome.status == "complete":
        return
    outcome.status = "failed"
    outcome.evaluated_at = None
    outcome.evidence = {
        "reason": reason,
        "retryable": False,
        "evaluator_version": EVALUATOR_VERSION,
        **(details or {}),
    }


def _apply_complete(
    outcome: MarketReportItemOutcome,
    *,
    payload: dict[str, Any],
    series: CandleSeries,
    candle: dict[str, object],
    moment: datetime,
) -> None:
    session_open = _decimal(candle.get("open"))
    session_high = _decimal(candle.get("high"))
    session_low = _decimal(candle.get("low"))
    session_close = _decimal(candle.get("close"))
    if None in {session_open, session_high, session_low, session_close}:
        _apply_pending(
            outcome,
            reason="incomplete_session_ohlc",
            details={"provider": series.provider},
        )
        return
    assert session_open is not None
    assert session_high is not None
    assert session_low is not None
    assert session_close is not None
    if session_low > session_high:
        _apply_pending(
            outcome,
            reason="invalid_session_range",
            details={"provider": series.provider},
        )
        return

    target_one, target_two, stop_loss = _prediction_levels(payload)
    return_bp = _basis_points(session_close, outcome.price_at_analysis)
    outcome.status = "complete"
    outcome.session_open = session_open
    outcome.session_high = session_high
    outcome.session_low = session_low
    outcome.session_close = session_close
    outcome.return_bp = return_bp
    outcome.max_upside_bp = _basis_points(session_high, outcome.price_at_analysis)
    outcome.max_drawdown_bp = _basis_points(session_low, outcome.price_at_analysis)
    outcome.direction_correct = _direction_correct(outcome.expected_direction, return_bp)
    outcome.target_one = target_one
    outcome.target_two = target_two
    outcome.stop_loss = stop_loss
    outcome.target_one_hit = _level_hit(
        target_one,
        expected_direction=outcome.expected_direction,
        session_high=session_high,
        session_low=session_low,
    )
    outcome.target_two_hit = _level_hit(
        target_two,
        expected_direction=outcome.expected_direction,
        session_high=session_high,
        session_low=session_low,
    )
    outcome.stop_loss_hit = _stop_hit(
        stop_loss,
        expected_direction=outcome.expected_direction,
        session_high=session_high,
        session_low=session_low,
    )
    outcome.provider = series.provider
    outcome.data_fingerprint = series.fingerprint
    outcome.data_as_of = series.data_as_of
    outcome.evaluated_at = moment
    outcome.evaluator_version = EVALUATOR_VERSION
    outcome.evidence = {
        "candle_timestamp": str(candle.get("timestamp", "")),
        "formula": "basis_points=(session_price/price_at_analysis-1)*10000",
        "negative_results_retained": True,
        "evaluator_version": EVALUATOR_VERSION,
    }


async def evaluate_market_report(
    db: Session,
    *,
    report_id: UUID,
    provider: MarketDataProvider,
    moment: datetime | None = None,
) -> ReportEvaluationResult:
    current = _aware(moment)
    calendar = EGXTradingCalendar.from_settings()
    report = _get_complete_report(db, report_id)
    if not _is_due(report.target_session_date, moment=current, calendar=calendar):
        raise ReportEvaluationNotDueError("Target EGX session has not closed yet")

    evaluation, idempotent = _start_evaluation(db, report=report, moment=current)
    if idempotent:
        return ReportEvaluationResult(
            evaluation=evaluation,
            outcomes=_outcomes_for_evaluation(db, evaluation.id),
            idempotent=True,
        )

    items = tuple(
        db.scalars(
            select(MarketReportItem)
            .where(MarketReportItem.report_id == report.id)
            .order_by(MarketReportItem.rank)
        ).all()
    )
    if not items:
        evaluation.status = "failed"
        evaluation.failed_count = 1
        evaluation.details = {
            "reason": "report_has_no_items",
            "evaluator_version": EVALUATOR_VERSION,
        }
        evaluation.completed_at = current
        db.commit()
        return ReportEvaluationResult(evaluation=evaluation, outcomes=(), idempotent=False)

    existing = {
        item.report_item_id: item
        for item in db.scalars(
            select(MarketReportItemOutcome).where(
                MarketReportItemOutcome.report_id == report.id
            )
        ).all()
    }
    pending_items = [item for item in items if existing.get(item.id) is None or existing[item.id].status != "complete"]
    semaphore = asyncio.Semaphore(4)
    fetched = await asyncio.gather(
        *(
            _fetch_series(provider, item.ticker, semaphore=semaphore)
            for item in pending_items
        ),
        return_exceptions=True,
    )

    for item, series_result in zip(pending_items, fetched, strict=True):
        payload = item.payload if isinstance(item.payload, dict) else {}
        price_at_analysis = _decimal(payload.get("price_at_analysis"))
        expected_direction = str(payload.get("expected_direction", "up")).lower()
        if expected_direction not in {"up", "down", "neutral"}:
            expected_direction = "up"
        outcome = existing.get(item.id)
        if outcome is None:
            if price_at_analysis is None:
                price_at_analysis = Decimal("1")
            outcome = _base_outcome(
                item,
                evaluation=evaluation,
                price_at_analysis=price_at_analysis,
                expected_direction=expected_direction,
            )
            db.add(outcome)
            existing[item.id] = outcome
        if outcome.status == "complete":
            continue
        if _decimal(payload.get("price_at_analysis")) is None:
            _apply_failed(outcome, reason="invalid_price_at_analysis")
            continue
        if isinstance(series_result, BaseException):
            _apply_pending(
                outcome,
                reason="market_data_unavailable",
                details={"error": type(series_result).__name__},
            )
            continue
        candle = _session_candle(
            series_result,
            target_session_date=report.target_session_date,
            calendar=calendar,
        )
        if candle is None:
            _apply_pending(
                outcome,
                reason="target_session_candle_missing",
                details={
                    "provider": series_result.provider,
                    "data_as_of": series_result.data_as_of.isoformat(),
                },
            )
            continue
        _apply_complete(
            outcome,
            payload=payload,
            series=series_result,
            candle=candle,
            moment=current,
        )

    db.flush()
    outcomes = _outcomes_for_evaluation(db, evaluation.id)
    evaluation.evaluated_count = sum(item.status == "complete" for item in outcomes)
    evaluation.pending_count = sum(item.status == "pending_data" for item in outcomes)
    evaluation.failed_count = sum(item.status == "failed" for item in outcomes)
    if evaluation.evaluated_count == len(items):
        evaluation.status = "complete"
        evaluation.completed_at = current
    elif evaluation.failed_count == len(items):
        evaluation.status = "failed"
        evaluation.completed_at = current
    else:
        evaluation.status = "partial"
        evaluation.completed_at = None
    evaluation.details = {
        "item_count": len(items),
        "evaluated_count": evaluation.evaluated_count,
        "pending_count": evaluation.pending_count,
        "failed_count": evaluation.failed_count,
        "negative_results_retained": True,
        "evaluator_version": EVALUATOR_VERSION,
    }
    db.commit()
    return ReportEvaluationResult(
        evaluation=evaluation,
        outcomes=_outcomes_for_evaluation(db, evaluation.id),
        idempotent=False,
    )


async def evaluate_due_market_reports(
    db: Session,
    *,
    provider: MarketDataProvider,
    moment: datetime | None = None,
    limit: int = 20,
) -> DueReportEvaluationResult:
    current = _aware(moment)
    calendar = EGXTradingCalendar.from_settings()
    reports = tuple(
        db.scalars(
            select(MarketReport)
            .where(MarketReport.status == "complete")
            .order_by(MarketReport.target_session_date, MarketReport.id)
            .limit(max(limit * 4, limit))
        ).all()
    )
    scanned = completed = partial = failed = skipped = 0
    evaluation_ids: list[UUID] = []
    for report in reports:
        if scanned >= limit:
            break
        if not _is_due(report.target_session_date, moment=current, calendar=calendar):
            skipped += 1
            continue
        current_evaluation = db.scalar(
            select(MarketReportEvaluation).where(
                MarketReportEvaluation.report_id == report.id
            )
        )
        if current_evaluation is not None and current_evaluation.status == "complete":
            skipped += 1
            continue
        scanned += 1
        try:
            result = await evaluate_market_report(
                db,
                report_id=report.id,
                provider=provider,
                moment=current,
            )
        except ReportEvaluationAlreadyRunningError:
            skipped += 1
            continue
        evaluation_ids.append(result.evaluation.id)
        if result.evaluation.status == "complete":
            completed += 1
        elif result.evaluation.status == "failed":
            failed += 1
        else:
            partial += 1
    return DueReportEvaluationResult(
        scanned_reports=scanned,
        completed_reports=completed,
        partial_reports=partial,
        failed_reports=failed,
        skipped_reports=skipped,
        evaluation_ids=tuple(evaluation_ids),
    )


def list_report_evaluations(
    db: Session,
    *,
    evaluation_status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[MarketReportEvaluation], int]:
    filters = []
    if evaluation_status:
        filters.append(MarketReportEvaluation.status == evaluation_status)
    total = int(
        db.scalar(select(func.count(MarketReportEvaluation.id)).where(*filters)) or 0
    )
    items = db.scalars(
        select(MarketReportEvaluation)
        .where(*filters)
        .order_by(
            MarketReportEvaluation.target_session_date.desc(),
            MarketReportEvaluation.id.desc(),
        )
        .limit(limit)
        .offset(offset)
    ).all()
    return list(items), total
