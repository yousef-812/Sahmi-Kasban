from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

import pandas as pd
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_data.catalog import ensure_market_instrument_catalog
from app.market_data.types import CandleSeries
from app.models import (
    AnalysisReplayJob,
    AnalysisReplayRow,
    AnalysisReplayTicker,
    MarketInstrumentCatalog,
)
from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer
from sahmi_kasban.indicators import prepare_candles

REPLAY_PARALLELISM = 5
REPLAY_MAX_RANGE_DAYS = 31


class HistoricalReplayError(RuntimeError):
    pass


class HistoricalReplayConflictError(HistoricalReplayError):
    pass


class HistoricalReplayNotFoundError(HistoricalReplayError):
    pass


@dataclass(frozen=True, slots=True)
class ReplayTickerComputation:
    ticker_task_id: UUID
    ticker: str
    provider: str | None
    data_fingerprint: str | None
    candle_count: int
    rows: tuple[dict[str, Any], ...]
    error_code: str | None = None
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class ReplayBatchPlan:
    job_id: UUID
    engine_version: str
    start_date: date
    end_date: date
    horizon_sessions: int
    min_train_size: int
    neutral_band_pct: float
    tasks: tuple[tuple[UUID, str], ...]


def _bp(value: float) -> int:
    return int(round(float(value) * 100.0))


def _pct(value: int | None) -> float | None:
    return None if value is None else round(value / 100.0, 2)


def _signature(
    *,
    actor_user_id: UUID,
    start_date: date,
    end_date: date,
    horizon_sessions: int,
    min_train_size: int,
    neutral_band_pct: float,
) -> str:
    payload = {
        "actor_user_id": str(actor_user_id),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "horizon_sessions": horizon_sessions,
        "min_train_size": min_train_size,
        "neutral_band_pct": round(neutral_band_pct, 4),
        "parallelism": REPLAY_PARALLELISM,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_historical_replay_job(
    db: Session,
    *,
    actor_user_id: UUID,
    request_key: str,
    start_date: date,
    end_date: date,
    horizon_sessions: int,
    min_train_size: int,
    neutral_band_pct: float,
) -> tuple[AnalysisReplayJob, bool]:
    if end_date < start_date or (end_date - start_date).days >= REPLAY_MAX_RANGE_DAYS:
        raise ValueError("الحد الأقصى لكل اختبار هو 31 يومًا")

    signature = _signature(
        actor_user_id=actor_user_id,
        start_date=start_date,
        end_date=end_date,
        horizon_sessions=horizon_sessions,
        min_train_size=min_train_size,
        neutral_band_pct=neutral_band_pct,
    )
    existing = db.scalar(
        select(AnalysisReplayJob).where(AnalysisReplayJob.request_key == request_key)
    )
    if existing is not None:
        if (
            existing.requested_by != actor_user_id
            or existing.details.get("request_signature") != signature
        ):
            raise HistoricalReplayConflictError(
                "مفتاح الطلب مستخدم بالفعل لاختبار تاريخي مختلف"
            )
        return existing, True

    settings = get_settings()
    job = AnalysisReplayJob(
        request_key=request_key,
        requested_by=actor_user_id,
        engine_version=settings.analysis_engine_version,
        status="pending",
        start_date=start_date,
        end_date=end_date,
        horizon_sessions=horizon_sessions,
        min_train_size=min_train_size,
        neutral_band_bp=_bp(neutral_band_pct),
        parallelism=REPLAY_PARALLELISM,
        total_tickers=0,
        processed_tickers=0,
        successful_tickers=0,
        failed_tickers=0,
        total_rows=0,
        evaluated_rows=0,
        pending_rows=0,
        details={
            "request_signature": signature,
            "history_visibility": "strictly_before_analysis_date",
            "provider_period": "5y",
        },
    )
    db.add(job)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raced = db.scalar(
            select(AnalysisReplayJob).where(
                AnalysisReplayJob.request_key == request_key
            )
        )
        if raced is None:
            raise
        if (
            raced.requested_by != actor_user_id
            or raced.details.get("request_signature") != signature
        ):
            raise HistoricalReplayConflictError(
                "مفتاح الطلب مستخدم بالفعل لاختبار تاريخي مختلف"
            ) from exc
        return raced, True
    db.refresh(job)
    return job, False


def get_historical_replay_job(
    db: Session,
    *,
    job_id: UUID,
    actor_user_id: UUID,
) -> AnalysisReplayJob:
    job = db.scalar(
        select(AnalysisReplayJob).where(
            AnalysisReplayJob.id == job_id,
            AnalysisReplayJob.requested_by == actor_user_id,
        )
    )
    if job is None:
        raise HistoricalReplayNotFoundError("الاختبار التاريخي غير موجود لهذا الحساب")
    return job


def list_historical_replay_jobs(
    db: Session,
    *,
    actor_user_id: UUID,
    limit: int,
    offset: int,
) -> tuple[list[AnalysisReplayJob], int]:
    filters = (AnalysisReplayJob.requested_by == actor_user_id,)
    total = int(
        db.scalar(select(func.count()).select_from(AnalysisReplayJob).where(*filters))
        or 0
    )
    items = db.scalars(
        select(AnalysisReplayJob)
        .where(*filters)
        .order_by(AnalysisReplayJob.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return list(items), total


def list_historical_replay_tickers(
    db: Session,
    *,
    job_id: UUID,
) -> list[AnalysisReplayTicker]:
    return list(
        db.scalars(
            select(AnalysisReplayTicker)
            .where(AnalysisReplayTicker.job_id == job_id)
            .order_by(AnalysisReplayTicker.ticker.asc())
        ).all()
    )


async def prepare_next_replay_batch(db: Session) -> ReplayBatchPlan | None:
    job = db.scalar(
        select(AnalysisReplayJob)
        .where(AnalysisReplayJob.status.in_(("pending", "running")))
        .order_by(AnalysisReplayJob.created_at.asc())
        .limit(1)
    )
    if job is None:
        return None

    now = datetime.now(UTC)
    if job.status == "pending":
        job.status = "running"
        job.started_at = job.started_at or now
    job.heartbeat_at = now

    await ensure_market_instrument_catalog(db)
    task_count = int(
        db.scalar(
            select(func.count())
            .select_from(AnalysisReplayTicker)
            .where(AnalysisReplayTicker.job_id == job.id)
        )
        or 0
    )
    if task_count == 0:
        tickers = list(
            db.scalars(
                select(MarketInstrumentCatalog.ticker)
                .where(MarketInstrumentCatalog.active.is_(True))
                .order_by(MarketInstrumentCatalog.ticker.asc())
            ).all()
        )
        for ticker in tickers:
            db.add(
                AnalysisReplayTicker(
                    job_id=job.id,
                    ticker=ticker,
                    status="pending",
                    candle_count=0,
                    rows_written=0,
                    evaluated_rows=0,
                    pending_rows=0,
                    failed_rows=0,
                )
            )
        job.total_tickers = len(tickers)
        db.flush()

    stale_before = now - timedelta(minutes=10)
    stale_tasks = db.scalars(
        select(AnalysisReplayTicker).where(
            AnalysisReplayTicker.job_id == job.id,
            AnalysisReplayTicker.status == "running",
            AnalysisReplayTicker.started_at < stale_before,
        )
    ).all()
    for task in stale_tasks:
        task.status = "pending"
        task.started_at = None

    tasks = list(
        db.scalars(
            select(AnalysisReplayTicker)
            .where(
                AnalysisReplayTicker.job_id == job.id,
                AnalysisReplayTicker.status == "pending",
            )
            .order_by(AnalysisReplayTicker.ticker.asc())
            .limit(REPLAY_PARALLELISM)
        ).all()
    )
    if not tasks:
        _refresh_job_totals(db, job)
        _finalize_job_if_done(db, job)
        db.commit()
        return None

    for task in tasks:
        task.status = "running"
        task.started_at = now
        task.completed_at = None
        task.error_code = None
        task.error_message = None
    db.commit()
    return ReplayBatchPlan(
        job_id=job.id,
        engine_version=job.engine_version,
        start_date=job.start_date,
        end_date=job.end_date,
        horizon_sessions=job.horizon_sessions,
        min_train_size=job.min_train_size,
        neutral_band_pct=job.neutral_band_bp / 100.0,
        tasks=tuple((task.id, task.ticker) for task in tasks),
    )


def compute_replay_rows(
    *,
    ticker_task_id: UUID,
    ticker: str,
    series: CandleSeries,
    engine_version: str,
    start_date: date,
    end_date: date,
    horizon_sessions: int,
    min_train_size: int,
    neutral_band_pct: float,
) -> ReplayTickerComputation:
    settings = get_settings()
    analyzer = SahmiKasbanAnalyzer(
        AnalysisConfig(
            capital=settings.analysis_default_capital,
            risk_per_trade=settings.analysis_risk_per_trade,
            max_position_value=settings.analysis_max_position_value,
            min_history=min_train_size,
        )
    )
    frame = prepare_candles(pd.DataFrame(series.candles))
    if "timestamp" not in frame.columns:
        raise ValueError("Market history is missing timestamps")

    session_dates = frame["timestamp"].dt.date
    target_indexes = [
        index
        for index, session_date in enumerate(session_dates)
        if start_date <= session_date <= end_date
    ]
    rows: list[dict[str, Any]] = []
    for cutoff in target_indexes:
        analysis_date = session_dates.iloc[cutoff]
        history = frame.iloc[:cutoff].copy()
        if len(history) < min_train_size:
            rows.append(
                {
                    "analysis_date": analysis_date,
                    "status": "skipped",
                    "engine_version": engine_version,
                    "provider": series.provider,
                    "data_fingerprint": series.fingerprint,
                    "data_as_of": None,
                    "candle_count": len(history),
                    "engines": {},
                    "trade_plan": None,
                    "warnings": [],
                    "analysis_quality": {},
                    "error_code": "insufficient_history",
                    "error_message": "البيانات السابقة لهذا اليوم أقل من الحد المطلوب للمحركات",
                }
            )
            continue

        data_as_of_value = history.iloc[-1]["timestamp"]
        data_as_of = data_as_of_value.to_pydatetime()
        try:
            report = analyzer.analyze(ticker, history)
        except Exception as exc:
            rows.append(
                {
                    "analysis_date": analysis_date,
                    "status": "failed",
                    "engine_version": engine_version,
                    "provider": series.provider,
                    "data_fingerprint": series.fingerprint,
                    "data_as_of": data_as_of,
                    "candle_count": len(history),
                    "engines": {},
                    "trade_plan": None,
                    "warnings": [],
                    "analysis_quality": {},
                    "error_code": type(exc).__name__[:64],
                    "error_message": str(exc)[:500],
                }
            )
            continue

        report_payload = report.to_dict()
        entry = float(history.iloc[-1]["close"])
        future = frame.iloc[cutoff : cutoff + horizon_sessions]
        row: dict[str, Any] = {
            "analysis_date": analysis_date,
            "status": "pending_evaluation",
            "engine_version": engine_version,
            "provider": series.provider,
            "data_fingerprint": series.fingerprint,
            "data_as_of": data_as_of,
            "candle_count": len(history),
            "signal": report.signal,
            "score_bp": _bp(report.final_score),
            "confidence_bp": _bp(report.confidence),
            "qualified": report.qualified,
            "engines": report_payload["engines"],
            "trade_plan": report_payload["trade_plan"],
            "warnings": report_payload["warnings"],
            "analysis_quality": report_payload["analysis_quality"],
            "entry": Decimal(str(round(entry, 6))),
            "evaluation_date": None,
            "exit": None,
            "forward_return_bp": None,
            "max_upside_bp": None,
            "max_drawdown_bp": None,
            "correct": None,
            "error_code": None,
            "error_message": None,
        }
        if len(future) >= horizon_sessions:
            exit_price = float(future.iloc[-1]["close"])
            forward_return = (exit_price / entry - 1.0) * 100.0
            max_upside = (float(future["high"].max()) / entry - 1.0) * 100.0
            max_drawdown = (float(future["low"].min()) / entry - 1.0) * 100.0
            if report.signal == "BUY":
                correct = forward_return > neutral_band_pct
            elif report.signal == "AVOID":
                correct = forward_return < -neutral_band_pct
            else:
                correct = abs(forward_return) <= neutral_band_pct
            row.update(
                {
                    "status": "evaluated",
                    "evaluation_date": future.iloc[-1]["timestamp"].date(),
                    "exit": Decimal(str(round(exit_price, 6))),
                    "forward_return_bp": _bp(forward_return),
                    "max_upside_bp": _bp(max_upside),
                    "max_drawdown_bp": _bp(max_drawdown),
                    "correct": correct,
                }
            )
        rows.append(row)

    return ReplayTickerComputation(
        ticker_task_id=ticker_task_id,
        ticker=ticker,
        provider=series.provider,
        data_fingerprint=series.fingerprint,
        candle_count=series.candle_count,
        rows=tuple(rows),
    )


def failed_ticker_computation(
    *,
    ticker_task_id: UUID,
    ticker: str,
    exc: Exception,
) -> ReplayTickerComputation:
    return ReplayTickerComputation(
        ticker_task_id=ticker_task_id,
        ticker=ticker,
        provider=None,
        data_fingerprint=None,
        candle_count=0,
        rows=(),
        error_code=type(exc).__name__[:64],
        error_message=str(exc)[:500],
    )


def persist_replay_batch(
    db: Session,
    *,
    job_id: UUID,
    computations: tuple[ReplayTickerComputation, ...],
) -> AnalysisReplayJob:
    job = db.get(AnalysisReplayJob, job_id)
    if job is None:
        raise HistoricalReplayNotFoundError("Historical replay job disappeared")

    for computation in computations:
        task = db.get(AnalysisReplayTicker, computation.ticker_task_id)
        if task is None or task.job_id != job_id:
            continue
        db.execute(
            delete(AnalysisReplayRow).where(
                AnalysisReplayRow.ticker_task_id == task.id
            )
        )
        if computation.error_code is not None:
            task.status = "failed"
            task.provider = computation.provider
            task.data_fingerprint = computation.data_fingerprint
            task.candle_count = computation.candle_count
            task.rows_written = 0
            task.evaluated_rows = 0
            task.pending_rows = 0
            task.failed_rows = 0
            task.error_code = computation.error_code
            task.error_message = computation.error_message
            task.completed_at = datetime.now(UTC)
            continue

        evaluated = 0
        pending = 0
        failed = 0
        for payload in computation.rows:
            status = str(payload["status"])
            evaluated += int(status == "evaluated")
            pending += int(status == "pending_evaluation")
            failed += int(status == "failed")
            db.add(
                AnalysisReplayRow(
                    job_id=job_id,
                    ticker_task_id=task.id,
                    ticker=computation.ticker,
                    **payload,
                )
            )
        task.status = "partial" if failed else "complete"
        task.provider = computation.provider
        task.data_fingerprint = computation.data_fingerprint
        task.candle_count = computation.candle_count
        task.rows_written = len(computation.rows)
        task.evaluated_rows = evaluated
        task.pending_rows = pending
        task.failed_rows = failed
        task.error_code = None
        task.error_message = None
        task.completed_at = datetime.now(UTC)

    job.heartbeat_at = datetime.now(UTC)
    _refresh_job_totals(db, job)
    _finalize_job_if_done(db, job)
    db.commit()
    db.refresh(job)
    return job


def _refresh_job_totals(db: Session, job: AnalysisReplayJob) -> None:
    task_rows = db.execute(
        select(
            func.count(AnalysisReplayTicker.id),
            func.count(AnalysisReplayTicker.id).filter(
                AnalysisReplayTicker.status.in_(("complete", "partial", "failed"))
            ),
            func.count(AnalysisReplayTicker.id).filter(
                AnalysisReplayTicker.status.in_(("complete", "partial"))
            ),
            func.count(AnalysisReplayTicker.id).filter(
                AnalysisReplayTicker.status == "failed"
            ),
            func.coalesce(func.sum(AnalysisReplayTicker.rows_written), 0),
            func.coalesce(func.sum(AnalysisReplayTicker.evaluated_rows), 0),
            func.coalesce(func.sum(AnalysisReplayTicker.pending_rows), 0),
        ).where(AnalysisReplayTicker.job_id == job.id)
    ).one()
    job.total_tickers = int(task_rows[0] or 0)
    job.processed_tickers = int(task_rows[1] or 0)
    job.successful_tickers = int(task_rows[2] or 0)
    job.failed_tickers = int(task_rows[3] or 0)
    job.total_rows = int(task_rows[4] or 0)
    job.evaluated_rows = int(task_rows[5] or 0)
    job.pending_rows = int(task_rows[6] or 0)


def _finalize_job_if_done(db: Session, job: AnalysisReplayJob) -> None:
    remaining = int(
        db.scalar(
            select(func.count())
            .select_from(AnalysisReplayTicker)
            .where(
                AnalysisReplayTicker.job_id == job.id,
                AnalysisReplayTicker.status.in_(("pending", "running")),
            )
        )
        or 0
    )
    if remaining:
        job.status = "running"
        return
    if job.total_tickers == 0:
        job.status = "failed"
        job.error_message = "لم يتم العثور على أسهم EGX نشطة للاختبار"
    elif job.failed_tickers == 0:
        job.status = "complete"
    elif job.successful_tickers > 0:
        job.status = "partial"
    else:
        job.status = "failed"
    job.completed_at = datetime.now(UTC)


def build_historical_replay_csv(
    db: Session,
    *,
    job: AnalysisReplayJob,
) -> bytes:
    rows = db.scalars(
        select(AnalysisReplayRow)
        .where(AnalysisReplayRow.job_id == job.id)
        .order_by(
            AnalysisReplayRow.analysis_date.asc(),
            AnalysisReplayRow.ticker.asc(),
        )
    ).all()
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "job_id",
            "engine_version",
            "ticker",
            "analysis_date",
            "status",
            "provider",
            "data_fingerprint",
            "data_as_of",
            "candle_count",
            "signal",
            "score",
            "confidence",
            "qualified",
            "entry",
            "evaluation_date",
            "exit",
            "forward_return_pct",
            "max_upside_pct",
            "max_drawdown_pct",
            "correct",
            "engines_json",
            "trade_plan_json",
            "warnings_json",
            "analysis_quality_json",
            "error_code",
            "error_message",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                str(job.id),
                row.engine_version,
                row.ticker,
                row.analysis_date.isoformat(),
                row.status,
                row.provider or "",
                row.data_fingerprint or "",
                row.data_as_of.isoformat() if row.data_as_of else "",
                row.candle_count,
                row.signal or "",
                _pct(row.score_bp) if row.score_bp is not None else "",
                _pct(row.confidence_bp) if row.confidence_bp is not None else "",
                row.qualified if row.qualified is not None else "",
                row.entry if row.entry is not None else "",
                row.evaluation_date.isoformat() if row.evaluation_date else "",
                row.exit if row.exit is not None else "",
                (
                    _pct(row.forward_return_bp)
                    if row.forward_return_bp is not None
                    else ""
                ),
                _pct(row.max_upside_bp) if row.max_upside_bp is not None else "",
                (
                    _pct(row.max_drawdown_bp)
                    if row.max_drawdown_bp is not None
                    else ""
                ),
                row.correct if row.correct is not None else "",
                json.dumps(row.engines, ensure_ascii=False, separators=(",", ":")),
                (
                    json.dumps(
                        row.trade_plan,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    if row.trade_plan
                    else ""
                ),
                json.dumps(row.warnings, ensure_ascii=False, separators=(",", ":")),
                json.dumps(
                    row.analysis_quality,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                row.error_code or "",
                row.error_message or "",
            ]
        )
    return ("\ufeff" + output.getvalue()).encode("utf-8")
