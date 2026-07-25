from __future__ import annotations

import asyncio
import json
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import UUID

import pandas as pd
from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer
from sahmi_kasban.ai import AIProviderError, SahmiAIService
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_calendar import EGXTradingCalendar, ScanSession
from app.market_data.egx_symbols import EGX_SEED_SYMBOLS
from app.market_data.types import MarketDataProvider
from app.models import (
    MarketReport,
    MarketReportItem,
    MarketReportUnlock,
    MarketScanRun,
    User,
)
from app.services.stock_analysis import DISCLAIMER_AR
from app.services.wallet import debit_points, get_wallet_account

logger = logging.getLogger(__name__)


class DailyReportError(RuntimeError):
    """Base error for generation and access to daily market reports."""


class DailyScanAlreadyRunningError(DailyReportError):
    """Raised when the same source session is currently being scanned."""


class DailyReportGenerationError(DailyReportError):
    """Raised when a complete top-ten report cannot be produced."""


class MarketReportNotFoundError(DailyReportError):
    """Raised when a requested complete report does not exist."""


class MarketReportLockedError(DailyReportError):
    """Raised when the user has not unlocked the requested report."""


@dataclass(frozen=True, slots=True)
class Candidate:
    ticker: str
    score_bp: int
    final_score: float
    confidence: float
    signal: str
    qualified: bool
    average_turnover_egp: float
    nonzero_volume_ratio: float
    last_close: float
    data_as_of: datetime
    provider: str
    fingerprint: str
    candle_count: int
    analysis: dict[str, Any]

    @property
    def sort_key(self) -> tuple[int, int, int, float, float]:
        signal_priority = {"BUY": 2, "WATCH": 1}.get(self.signal, 0)
        return (
            int(self.qualified),
            signal_priority,
            self.score_bp,
            self.confidence,
            self.average_turnover_egp,
        )


@dataclass(frozen=True, slots=True)
class CandidateOutcome:
    ticker: str
    candidate: Candidate | None = None
    excluded_reason: str | None = None
    failure: str | None = None


@dataclass(frozen=True, slots=True)
class DailyReportGenerationResult:
    report: MarketReport
    scan_run: MarketScanRun
    created: bool


@dataclass(frozen=True, slots=True)
class MarketReportAccess:
    report: MarketReport
    items: tuple[MarketReportItem, ...]
    unlocked: bool


@dataclass(frozen=True, slots=True)
class MarketReportUnlockExecution:
    access: MarketReportAccess
    charged_points: int
    balance_points: int


def _json_default(value: Any) -> object:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    item = getattr(value, "item", None)
    if callable(item):
        return item()
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        return tolist()
    raise TypeError(f"Unsupported JSON value: {type(value).__name__}")


def _json_safe(value: object) -> object:
    return json.loads(json.dumps(value, default=_json_default, ensure_ascii=False))


def _number(payload: dict[str, Any], key: str) -> float:
    try:
        return float(payload.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _deterministic_explanation(candidate: Candidate) -> str:
    decision = {"BUY": "فرصة قوية بشروط المخاطر", "WATCH": "فرصة للمراقبة"}.get(
        candidate.signal,
        candidate.signal,
    )
    return (
        f"{decision}. الدرجة {candidate.final_score:.1f} من 100، "
        f"والثقة {candidate.confidence:.1f}%. متوسط السيولة اليومية التقديري "
        f"{candidate.average_turnover_egp:,.0f} جنيه. راجع الدخول ووقف الخسارة "
        "والأهداف داخل تفاصيل التقرير."
    )


def _report_items(db: Session, report_id: UUID) -> tuple[MarketReportItem, ...]:
    return tuple(
        db.scalars(
            select(MarketReportItem)
            .where(MarketReportItem.report_id == report_id)
            .order_by(MarketReportItem.rank)
        ).all()
    )


def _complete_report_for_target(db: Session, target_date: date) -> MarketReport | None:
    return db.scalar(
        select(MarketReport).where(
            MarketReport.target_session_date == target_date,
            MarketReport.status == "complete",
        )
    )


def latest_complete_report(db: Session) -> MarketReport:
    report = db.scalar(
        select(MarketReport)
        .where(MarketReport.status == "complete")
        .order_by(MarketReport.target_session_date.desc())
        .limit(1)
    )
    if report is None:
        raise MarketReportNotFoundError("No complete market report is available")
    return report


def get_complete_report(db: Session, report_id: UUID) -> MarketReport:
    report = db.scalar(
        select(MarketReport).where(
            MarketReport.id == report_id,
            MarketReport.status == "complete",
        )
    )
    if report is None:
        raise MarketReportNotFoundError("Market report was not found")
    return report


def report_is_unlocked(db: Session, *, user_id: UUID, report_id: UUID) -> bool:
    return (
        db.scalar(
            select(MarketReportUnlock.id).where(
                MarketReportUnlock.user_id == user_id,
                MarketReportUnlock.report_id == report_id,
            )
        )
        is not None
    )


def get_report_access(
    db: Session,
    *,
    user_id: UUID,
    report_id: UUID,
    require_unlock: bool,
) -> MarketReportAccess:
    report = get_complete_report(db, report_id)
    unlocked = report_is_unlocked(db, user_id=user_id, report_id=report.id)
    if require_unlock and not unlocked:
        raise MarketReportLockedError("Market report has not been unlocked")
    return MarketReportAccess(
        report=report,
        items=_report_items(db, report.id) if unlocked or not require_unlock else (),
        unlocked=unlocked,
    )


def unlock_market_report(
    db: Session,
    *,
    user: User,
    report_id: UUID,
) -> MarketReportUnlockExecution:
    settings = get_settings()
    report = get_complete_report(db, report_id)
    existing = db.scalar(
        select(MarketReportUnlock).where(
            MarketReportUnlock.user_id == user.id,
            MarketReportUnlock.report_id == report.id,
        )
    )
    if existing is not None:
        account = get_wallet_account(db, user.id)
        return MarketReportUnlockExecution(
            access=MarketReportAccess(
                report=report,
                items=_report_items(db, report.id),
                unlocked=True,
            ),
            charged_points=0,
            balance_points=account.balance_points,
        )

    items = _report_items(db, report.id)
    if len(items) != settings.daily_report_size:
        raise DailyReportGenerationError("Market report is incomplete and cannot be sold")

    transaction_id = f"market-report:{user.id}:{report.id}"
    try:
        debit_points(
            db,
            user_id=user.id,
            amount_points=settings.daily_report_cost_points,
            transaction_id=transaction_id,
            entry_type="market_report_debit",
            reference_type="market_report",
            reference_id=str(report.id),
            details={
                "target_session_date": report.target_session_date.isoformat(),
            },
        )
        db.add(
            MarketReportUnlock(
                user_id=user.id,
                report_id=report.id,
                wallet_transaction_id=transaction_id,
                unlocked_at=datetime.now(UTC),
            )
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raced = db.scalar(
            select(MarketReportUnlock).where(
                MarketReportUnlock.user_id == user.id,
                MarketReportUnlock.report_id == report.id,
            )
        )
        if raced is None:
            raise
        account = get_wallet_account(db, user.id)
        return MarketReportUnlockExecution(
            access=MarketReportAccess(report=report, items=items, unlocked=True),
            charged_points=0,
            balance_points=account.balance_points,
        )
    except Exception:
        db.rollback()
        raise

    account = get_wallet_account(db, user.id)
    return MarketReportUnlockExecution(
        access=MarketReportAccess(report=report, items=items, unlocked=True),
        charged_points=settings.daily_report_cost_points,
        balance_points=account.balance_points,
    )


async def _analyze_ticker(
    ticker: str,
    *,
    source_session_date: date,
    provider: MarketDataProvider,
    semaphore: asyncio.Semaphore,
) -> CandidateOutcome:
    settings = get_settings()
    try:
        async with semaphore:
            series = await provider.get_history(
                ticker,
                period=settings.market_data_period,
                interval=settings.market_data_interval,
            )
    except Exception as exc:
        logger.info("Daily scan data failure for %s: %s", ticker, exc)
        return CandidateOutcome(ticker=ticker, failure=type(exc).__name__)

    calendar = EGXTradingCalendar.from_settings()
    data_session_date = series.data_as_of.astimezone(calendar.timezone).date()
    if data_session_date != source_session_date:
        return CandidateOutcome(ticker=ticker, excluded_reason="stale_close")

    frame = pd.DataFrame(series.candles)
    if len(frame) < settings.market_data_min_candles:
        return CandidateOutcome(ticker=ticker, excluded_reason="insufficient_history")

    recent = frame.tail(20).copy()
    recent["close"] = pd.to_numeric(recent["close"], errors="coerce")
    recent["volume"] = pd.to_numeric(recent["volume"], errors="coerce").fillna(0)
    turnover = (recent["close"] * recent["volume"]).dropna()
    average_turnover = float(turnover.mean()) if not turnover.empty else 0.0
    nonzero_volume_ratio = float((recent["volume"] > 0).mean())
    if average_turnover < settings.daily_scan_min_average_turnover_egp:
        return CandidateOutcome(ticker=ticker, excluded_reason="low_turnover")
    if nonzero_volume_ratio < settings.daily_scan_min_nonzero_volume_ratio:
        return CandidateOutcome(ticker=ticker, excluded_reason="thin_volume_history")

    config = AnalysisConfig(
        capital=settings.analysis_default_capital,
        risk_per_trade=settings.analysis_risk_per_trade,
        max_position_value=settings.analysis_max_position_value,
        min_history=settings.market_data_min_candles,
    )
    try:
        analyzer = SahmiKasbanAnalyzer(config)
        report = await asyncio.to_thread(analyzer.analyze, series.ticker, frame)
        raw_payload = _json_safe(report.to_dict())
    except Exception as exc:
        logger.info("Daily scan engine failure for %s: %s", ticker, exc)
        return CandidateOutcome(ticker=ticker, failure=type(exc).__name__)
    if not isinstance(raw_payload, dict):
        return CandidateOutcome(ticker=ticker, failure="invalid_analysis_payload")

    signal = str(raw_payload.get("signal", "AVOID")).upper()
    if signal not in {"BUY", "WATCH"}:
        return CandidateOutcome(ticker=ticker, excluded_reason="avoid_signal")
    final_score = max(0.0, min(100.0, _number(raw_payload, "final_score")))
    confidence = max(0.0, min(100.0, _number(raw_payload, "confidence")))
    score_bp = int(round(final_score * 100))
    candidate = Candidate(
        ticker=series.ticker,
        score_bp=score_bp,
        final_score=final_score,
        confidence=confidence,
        signal=signal,
        qualified=bool(raw_payload.get("qualified", False)),
        average_turnover_egp=average_turnover,
        nonzero_volume_ratio=nonzero_volume_ratio,
        last_close=float(frame.iloc[-1]["close"]),
        data_as_of=series.data_as_of,
        provider=series.provider,
        fingerprint=series.fingerprint,
        candle_count=series.candle_count,
        analysis=raw_payload,
    )
    return CandidateOutcome(ticker=ticker, candidate=candidate)


async def _explain_candidate(
    candidate: Candidate,
    *,
    ai_service: SahmiAIService,
    semaphore: asyncio.Semaphore,
) -> tuple[str, str]:
    explanation = _deterministic_explanation(candidate)
    source = "deterministic"
    try:
        async with semaphore:
            explanation = await ai_service.explain_stock_analysis(
                ticker=candidate.ticker,
                analysis_payload=candidate.analysis,
                language="ar",
            )
        source = "ai"
    except AIProviderError as exc:
        logger.info("Daily report AI fallback for %s: %s", candidate.ticker, exc)
    return explanation, source


def _start_scan_run(db: Session, session: ScanSession, total_symbols: int) -> MarketScanRun:
    existing = db.scalar(
        select(MarketScanRun)
        .where(MarketScanRun.source_session_date == session.source_session_date)
        .with_for_update()
    )
    now = datetime.now(UTC)
    if existing is not None:
        if existing.status == "complete":
            return existing
        if existing.status == "running" and existing.started_at > now - timedelta(hours=3):
            raise DailyScanAlreadyRunningError("Daily scan is already running")
        existing.status = "running"
        existing.started_at = now
        existing.completed_at = None
        existing.target_session_date = session.target_session_date
        existing.total_symbols = total_symbols
        existing.analyzed_count = 0
        existing.eligible_count = 0
        existing.failed_count = 0
        existing.details = {}
        db.commit()
        return existing

    run = MarketScanRun(
        source_session_date=session.source_session_date,
        target_session_date=session.target_session_date,
        scheduled_for=session.scheduled_for,
        started_at=now,
        status="running",
        total_symbols=total_symbols,
        analyzed_count=0,
        eligible_count=0,
        failed_count=0,
        details={},
    )
    db.add(run)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DailyScanAlreadyRunningError("Daily scan was started concurrently") from exc
    return run


def _mark_scan_failed(
    db: Session,
    run_id: UUID,
    *,
    reason: str,
    analyzed_count: int = 0,
    eligible_count: int = 0,
    failed_count: int = 0,
    details: dict[str, Any] | None = None,
) -> None:
    run = db.get(MarketScanRun, run_id)
    if run is None:
        return
    run.status = "failed"
    run.completed_at = datetime.now(UTC)
    run.analyzed_count = analyzed_count
    run.eligible_count = eligible_count
    run.failed_count = failed_count
    run.details = {"reason": reason, **(details or {})}
    db.commit()


async def generate_daily_top10_report(
    db: Session,
    *,
    provider: MarketDataProvider,
    ai_service: SahmiAIService,
    moment: datetime | None = None,
    tickers: tuple[str, ...] = EGX_SEED_SYMBOLS,
) -> DailyReportGenerationResult:
    settings = get_settings()
    calendar = EGXTradingCalendar.from_settings()
    session = calendar.resolve_scan_session(moment)
    existing_report = _complete_report_for_target(db, session.target_session_date)
    if existing_report is not None:
        run = db.scalar(
            select(MarketScanRun).where(
                MarketScanRun.source_session_date == session.source_session_date
            )
        )
        if run is None:
            raise DailyReportGenerationError("Report exists without a scan audit record")
        return DailyReportGenerationResult(report=existing_report, scan_run=run, created=False)

    run = _start_scan_run(db, session, len(tickers))
    if run.status == "complete":
        report = _complete_report_for_target(db, session.target_session_date)
        if report is None:
            raise DailyReportGenerationError("Completed scan has no market report")
        return DailyReportGenerationResult(report=report, scan_run=run, created=False)

    semaphore = asyncio.Semaphore(settings.daily_scan_max_concurrency)
    outcomes = await asyncio.gather(
        *(
            _analyze_ticker(
                ticker,
                source_session_date=session.source_session_date,
                provider=provider,
                semaphore=semaphore,
            )
            for ticker in tickers
        )
    )
    candidates = [outcome.candidate for outcome in outcomes if outcome.candidate]
    candidates.sort(key=lambda candidate: candidate.sort_key, reverse=True)
    failures = {
        outcome.ticker: outcome.failure
        for outcome in outcomes
        if outcome.failure is not None
    }
    exclusions = Counter(
        outcome.excluded_reason
        for outcome in outcomes
        if outcome.excluded_reason is not None
    )
    analyzed_count = len(tickers) - len(failures)
    if len(candidates) < settings.daily_report_size:
        _mark_scan_failed(
            db,
            run.id,
            reason="not_enough_eligible_candidates",
            analyzed_count=analyzed_count,
            eligible_count=len(candidates),
            failed_count=len(failures),
            details={
                "exclusions": dict(exclusions),
                "failures": failures,
            },
        )
        raise DailyReportGenerationError(
            f"Only {len(candidates)} eligible candidates were produced"
        )

    selected = candidates[: settings.daily_report_size]
    ai_semaphore = asyncio.Semaphore(2)
    explanations = await asyncio.gather(
        *(
            _explain_candidate(
                candidate,
                ai_service=ai_service,
                semaphore=ai_semaphore,
            )
            for candidate in selected
        )
    )

    generated_at = datetime.now(UTC)
    report = MarketReport(
        target_session_date=session.target_session_date,
        status="complete",
        generated_at=generated_at,
        source_snapshot={
            "source_session_date": session.source_session_date.isoformat(),
            "scheduled_for": session.scheduled_for.isoformat(),
            "universe_size": len(tickers),
            "engine_version": settings.analysis_engine_version,
            "providers": sorted({candidate.provider for candidate in selected}),
            "top_fingerprints": {
                candidate.ticker: candidate.fingerprint for candidate in selected
            },
        },
        market_summary={
            "title": "الأسهم الأعلى تقييمًا وفق التحليل الآلي للجلسة القادمة",
            "source_session_date": session.source_session_date.isoformat(),
            "target_session_date": session.target_session_date.isoformat(),
            "analyzed_count": analyzed_count,
            "eligible_count": len(candidates),
            "failed_count": len(failures),
            "average_top_score": round(
                sum(candidate.final_score for candidate in selected) / len(selected),
                2,
            ),
            "signals": dict(Counter(candidate.signal for candidate in selected)),
            "disclaimer": DISCLAIMER_AR,
        },
    )
    db.add(report)
    try:
        db.flush()
        for rank, (candidate, explanation_data) in enumerate(
            zip(selected, explanations, strict=True),
            start=1,
        ):
            explanation, explanation_source = explanation_data
            db.add(
                MarketReportItem(
                    report_id=report.id,
                    ticker=candidate.ticker,
                    rank=rank,
                    score_bp=candidate.score_bp,
                    payload={
                        "ticker": candidate.ticker,
                        "rank": rank,
                        "price_at_analysis": round(candidate.last_close, 6),
                        "score": round(candidate.final_score, 2),
                        "signal": candidate.signal,
                        "decision": (
                            "فرصة قوية" if candidate.signal == "BUY" else "مراقبة"
                        ),
                        "expected_direction": "up",
                        "confidence": round(candidate.confidence, 2),
                        "qualified": candidate.qualified,
                        "liquidity": {
                            "average_turnover_egp_20d": round(
                                candidate.average_turnover_egp,
                                2,
                            ),
                            "nonzero_volume_ratio_20d": round(
                                candidate.nonzero_volume_ratio,
                                4,
                            ),
                        },
                        "market_data": {
                            "provider": candidate.provider,
                            "data_as_of": candidate.data_as_of.isoformat(),
                            "fingerprint": candidate.fingerprint,
                            "candle_count": candidate.candle_count,
                        },
                        "analysis": candidate.analysis,
                        "explanation": explanation,
                        "explanation_source": explanation_source,
                        "disclaimer": DISCLAIMER_AR,
                    },
                )
            )
        locked_run = db.scalar(
            select(MarketScanRun)
            .where(MarketScanRun.id == run.id)
            .with_for_update()
        )
        if locked_run is None:
            raise DailyReportGenerationError("Scan audit record disappeared")
        locked_run.status = "complete"
        locked_run.completed_at = generated_at
        locked_run.analyzed_count = analyzed_count
        locked_run.eligible_count = len(candidates)
        locked_run.failed_count = len(failures)
        locked_run.details = {
            "report_id": str(report.id),
            "selected_tickers": [candidate.ticker for candidate in selected],
            "exclusions": dict(exclusions),
            "failures": failures,
        }
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raced = _complete_report_for_target(db, session.target_session_date)
        if raced is None:
            _mark_scan_failed(db, run.id, reason="database_integrity_error")
            raise
        refreshed_run = db.get(MarketScanRun, run.id)
        if refreshed_run is None:
            raise DailyReportGenerationError(
                "Concurrent report has no scan record"
            ) from exc
        return DailyReportGenerationResult(
            report=raced,
            scan_run=refreshed_run,
            created=False,
        )
    except Exception as exc:
        db.rollback()
        _mark_scan_failed(
            db,
            run.id,
            reason=type(exc).__name__,
            analyzed_count=analyzed_count,
            eligible_count=len(candidates),
            failed_count=len(failures),
            details={
                "exclusions": dict(exclusions),
                "failures": failures,
            },
        )
        raise

    return DailyReportGenerationResult(report=report, scan_run=run, created=True)
