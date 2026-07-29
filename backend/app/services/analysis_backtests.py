from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.market_data.types import MarketDataProvider
from app.models import (
    AnalysisBacktestObservation,
    AnalysisBacktestResult,
    AnalysisBacktestRun,
)
from sahmi_kasban import (
    AnalysisConfig,
    BacktestSummary,
    SahmiKasbanAnalyzer,
    walk_forward_backtest,
)


class AnalysisBacktestError(RuntimeError):
    """Base error for persisted historical validation."""


class AnalysisBacktestConflictError(AnalysisBacktestError):
    """Raised when an idempotency key is reused with different parameters."""


class AnalysisBacktestNotFoundError(AnalysisBacktestError):
    """Raised when a requested backtest run does not exist."""


@dataclass(frozen=True, slots=True)
class AnalysisBacktestExecution:
    run: AnalysisBacktestRun
    results: tuple[AnalysisBacktestResult, ...]
    idempotent: bool


def _normalize_tickers(tickers: list[str]) -> list[str]:
    normalized = [ticker.strip().upper() for ticker in tickers if ticker.strip()]
    if not 1 <= len(normalized) <= 3:
        raise ValueError("Backtest runs require between one and three tickers")
    if len(set(normalized)) != len(normalized):
        raise ValueError("Backtest tickers must be unique")
    return normalized


def _request_signature(
    *,
    engine_version: str,
    tickers: list[str],
    period: str,
    interval: str,
    min_train_size: int,
    horizon_sessions: int,
    step_sessions: int,
    neutral_band_pct: float,
) -> str:
    identity = {
        "engine_version": engine_version,
        "tickers": tickers,
        "period": period,
        "interval": interval,
        "min_train_size": min_train_size,
        "horizon_sessions": horizon_sessions,
        "step_sessions": step_sessions,
        "neutral_band_pct": round(neutral_band_pct, 4),
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _percent_to_bp(value: float) -> int:
    return int(round(float(value) * 100.0))


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _result_rows(
    db: Session,
    *,
    run: AnalysisBacktestRun,
) -> tuple[AnalysisBacktestResult, ...]:
    return tuple(
        db.scalars(
            select(AnalysisBacktestResult)
            .where(AnalysisBacktestResult.run_id == run.id)
            .order_by(AnalysisBacktestResult.ticker.asc())
        ).all()
    )


def _summary_payload(summary: BacktestSummary) -> dict[str, object]:
    return summary.to_dict(include_results=False)


def _complete_result(
    db: Session,
    *,
    run: AnalysisBacktestRun,
    series,
    summary: BacktestSummary,
) -> AnalysisBacktestResult:
    result = AnalysisBacktestResult(
        run_id=run.id,
        ticker=summary.ticker,
        status="complete",
        provider=series.provider,
        data_fingerprint=series.fingerprint,
        data_as_of=series.data_as_of,
        candle_count=series.candle_count,
        observations=summary.observations,
        buy_count=summary.buy_count,
        watch_count=summary.watch_count,
        avoid_count=summary.avoid_count,
        directional_accuracy_bp=_percent_to_bp(summary.directional_accuracy_pct),
        buy_hit_rate_bp=_percent_to_bp(summary.buy_hit_rate_pct),
        avoid_hit_rate_bp=_percent_to_bp(summary.avoid_hit_rate_pct),
        watch_hit_rate_bp=_percent_to_bp(summary.watch_hit_rate_pct),
        average_forward_return_bp=_percent_to_bp(summary.average_forward_return_pct),
        median_forward_return_bp=_percent_to_bp(summary.median_forward_return_pct),
        average_buy_return_bp=_percent_to_bp(summary.average_buy_return_pct),
        average_buy_max_drawdown_bp=_percent_to_bp(
            summary.average_buy_max_drawdown_pct
        ),
        profit_factor_milli=(
            None
            if summary.profit_factor is None
            else int(round(summary.profit_factor * 1000.0))
        ),
        summary=_summary_payload(summary),
    )
    db.add(result)
    db.flush()

    for observation in summary.results:
        db.add(
            AnalysisBacktestObservation(
                result_id=result.id,
                cutoff_index=observation.cutoff_index,
                data_as_of=_parse_datetime(observation.data_as_of),
                signal=observation.signal,
                score_bp=_percent_to_bp(observation.score),
                confidence_bp=_percent_to_bp(observation.confidence),
                entry=Decimal(str(observation.entry)),
                exit=Decimal(str(observation.exit)),
                forward_return_bp=_percent_to_bp(observation.forward_return_pct),
                max_upside_bp=_percent_to_bp(observation.max_upside_pct),
                max_drawdown_bp=_percent_to_bp(observation.max_drawdown_pct),
                correct=observation.correct,
            )
        )
    db.flush()
    return result


def _failed_result(
    db: Session,
    *,
    run: AnalysisBacktestRun,
    ticker: str,
    exc: Exception,
) -> AnalysisBacktestResult:
    result = AnalysisBacktestResult(
        run_id=run.id,
        ticker=ticker,
        status="failed",
        candle_count=0,
        observations=0,
        buy_count=0,
        watch_count=0,
        avoid_count=0,
        directional_accuracy_bp=0,
        buy_hit_rate_bp=0,
        avoid_hit_rate_bp=0,
        watch_hit_rate_bp=0,
        average_forward_return_bp=0,
        median_forward_return_bp=0,
        average_buy_return_bp=0,
        average_buy_max_drawdown_bp=0,
        error_code=type(exc).__name__[:64],
        error_message=str(exc)[:500],
        summary={},
    )
    db.add(result)
    db.flush()
    return result


async def execute_analysis_backtest(
    db: Session,
    *,
    actor_user_id: UUID | None,
    request_key: str,
    tickers: list[str],
    provider: MarketDataProvider,
    period: str = "5y",
    interval: str = "1d",
    min_train_size: int = 200,
    horizon_sessions: int = 5,
    step_sessions: int = 20,
    neutral_band_pct: float = 1.0,
) -> AnalysisBacktestExecution:
    settings = get_settings()
    normalized_tickers = _normalize_tickers(tickers)
    signature = _request_signature(
        engine_version=settings.analysis_engine_version,
        tickers=normalized_tickers,
        period=period,
        interval=interval,
        min_train_size=min_train_size,
        horizon_sessions=horizon_sessions,
        step_sessions=step_sessions,
        neutral_band_pct=neutral_band_pct,
    )
    existing = db.scalar(
        select(AnalysisBacktestRun).where(
            AnalysisBacktestRun.request_key == request_key
        )
    )
    if existing is not None:
        if existing.details.get("request_signature") != signature:
            raise AnalysisBacktestConflictError(
                "The request key is already used for a different backtest"
            )
        return AnalysisBacktestExecution(
            run=existing,
            results=_result_rows(db, run=existing),
            idempotent=True,
        )

    started_at = datetime.now(UTC)
    run = AnalysisBacktestRun(
        request_key=request_key,
        engine_version=settings.analysis_engine_version,
        status="running",
        tickers=normalized_tickers,
        period=period,
        interval=interval,
        min_train_size=min_train_size,
        horizon_sessions=horizon_sessions,
        step_sessions=step_sessions,
        neutral_band_bp=_percent_to_bp(neutral_band_pct),
        total_tickers=len(normalized_tickers),
        completed_tickers=0,
        failed_tickers=0,
        requested_by=actor_user_id,
        started_at=started_at,
        details={"request_signature": signature},
    )
    db.add(run)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raced = db.scalar(
            select(AnalysisBacktestRun).where(
                AnalysisBacktestRun.request_key == request_key
            )
        )
        if raced is None:
            raise
        if raced.details.get("request_signature") != signature:
            raise AnalysisBacktestConflictError(
                "The request key is already used for a different backtest"
            ) from exc
        return AnalysisBacktestExecution(
            run=raced,
            results=_result_rows(db, run=raced),
            idempotent=True,
        )

    run_id = run.id
    analyzer = SahmiKasbanAnalyzer(
        AnalysisConfig(
            capital=settings.analysis_default_capital,
            risk_per_trade=settings.analysis_risk_per_trade,
            max_position_value=settings.analysis_max_position_value,
            min_history=min_train_size,
        )
    )
    completed = 0
    failed = 0
    failures: list[dict[str, str]] = []

    for ticker in normalized_tickers:
        try:
            series = await provider.get_history(
                ticker,
                period=period,
                interval=interval,
            )
            summary = walk_forward_backtest(
                ticker,
                pd.DataFrame(series.candles),
                analyzer=analyzer,
                min_train_size=min_train_size,
                horizon_sessions=horizon_sessions,
                step_sessions=step_sessions,
                neutral_band_pct=neutral_band_pct,
            )
            _complete_result(db, run=run, series=series, summary=summary)
            completed += 1
        except Exception as exc:
            db.rollback()
            run = db.get(AnalysisBacktestRun, run_id)
            if run is None:
                raise
            _failed_result(db, run=run, ticker=ticker, exc=exc)
            failed += 1
            failures.append(
                {
                    "ticker": ticker,
                    "error_code": type(exc).__name__,
                    "message": str(exc)[:500],
                }
            )

        run.completed_tickers = completed
        run.failed_tickers = failed
        run.details = {
            "request_signature": signature,
            "failures": failures,
        }
        db.commit()

    run.status = (
        "complete"
        if completed == len(normalized_tickers)
        else "partial"
        if completed
        else "failed"
    )
    run.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(run)
    return AnalysisBacktestExecution(
        run=run,
        results=_result_rows(db, run=run),
        idempotent=False,
    )


def get_analysis_backtest_run(
    db: Session,
    *,
    run_id: UUID,
) -> AnalysisBacktestExecution:
    run = db.get(AnalysisBacktestRun, run_id)
    if run is None:
        raise AnalysisBacktestNotFoundError("Backtest run was not found")
    return AnalysisBacktestExecution(
        run=run,
        results=_result_rows(db, run=run),
        idempotent=False,
    )


def list_analysis_backtest_runs(
    db: Session,
    *,
    run_status: str | None,
    engine_version: str | None,
    limit: int,
    offset: int,
) -> tuple[list[AnalysisBacktestRun], int]:
    filters = []
    if run_status:
        filters.append(AnalysisBacktestRun.status == run_status)
    if engine_version:
        filters.append(AnalysisBacktestRun.engine_version == engine_version)

    total = int(
        db.scalar(
            select(func.count())
            .select_from(AnalysisBacktestRun)
            .where(*filters)
        )
        or 0
    )
    items = db.scalars(
        select(AnalysisBacktestRun)
        .where(*filters)
        .order_by(AnalysisBacktestRun.started_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return list(items), total


def analysis_backtest_version_summaries(db: Session) -> list[dict[str, Any]]:
    rows = db.execute(
        select(AnalysisBacktestRun, AnalysisBacktestResult)
        .join(
            AnalysisBacktestResult,
            AnalysisBacktestResult.run_id == AnalysisBacktestRun.id,
        )
        .where(AnalysisBacktestResult.status == "complete")
        .order_by(AnalysisBacktestRun.engine_version.asc())
    ).all()
    grouped: dict[str, dict[str, Any]] = {}
    for run, result in rows:
        item = grouped.setdefault(
            run.engine_version,
            {
                "engine_version": run.engine_version,
                "run_ids": set(),
                "tickers": 0,
                "observations": 0,
                "buy_count": 0,
                "watch_count": 0,
                "avoid_count": 0,
                "directional_weighted": 0,
                "directional_weight": 0,
                "buy_hit_weighted": 0,
                "buy_weight": 0,
                "forward_weighted": 0,
                "buy_return_weighted": 0,
                "drawdown_weighted": 0,
                "profit_factor_weighted": 0,
                "profit_factor_weight": 0,
            },
        )
        observations = result.observations
        directional_weight = result.buy_count + result.avoid_count
        buy_weight = result.buy_count
        item["run_ids"].add(run.id)
        item["tickers"] += 1
        item["observations"] += observations
        item["buy_count"] += result.buy_count
        item["watch_count"] += result.watch_count
        item["avoid_count"] += result.avoid_count
        if directional_weight > 0:
            item["directional_weighted"] += (
                result.directional_accuracy_bp * directional_weight
            )
            item["directional_weight"] += directional_weight
        if buy_weight > 0:
            item["buy_hit_weighted"] += result.buy_hit_rate_bp * buy_weight
            item["buy_return_weighted"] += (
                result.average_buy_return_bp * buy_weight
            )
            item["drawdown_weighted"] += (
                result.average_buy_max_drawdown_bp * buy_weight
            )
            item["buy_weight"] += buy_weight
        item["forward_weighted"] += (
            result.average_forward_return_bp * observations
        )
        if result.profit_factor_milli is not None and buy_weight > 0:
            item["profit_factor_weighted"] += (
                result.profit_factor_milli * buy_weight
            )
            item["profit_factor_weight"] += buy_weight

    summaries: list[dict[str, Any]] = []
    for item in grouped.values():
        observation_weight = max(item["observations"], 1)
        directional_weight = item["directional_weight"]
        buy_weight = item["buy_weight"]
        summaries.append(
            {
                "engine_version": item["engine_version"],
                "runs": len(item["run_ids"]),
                "tickers": item["tickers"],
                "observations": item["observations"],
                "buy_count": item["buy_count"],
                "watch_count": item["watch_count"],
                "avoid_count": item["avoid_count"],
                "directional_accuracy_pct": (
                    0.0
                    if directional_weight <= 0
                    else round(
                        item["directional_weighted"]
                        / directional_weight
                        / 100.0,
                        2,
                    )
                ),
                "buy_hit_rate_pct": (
                    0.0
                    if buy_weight <= 0
                    else round(
                        item["buy_hit_weighted"] / buy_weight / 100.0,
                        2,
                    )
                ),
                "average_forward_return_pct": round(
                    item["forward_weighted"] / observation_weight / 100.0,
                    2,
                ),
                "average_buy_return_pct": (
                    0.0
                    if buy_weight <= 0
                    else round(
                        item["buy_return_weighted"] / buy_weight / 100.0,
                        2,
                    )
                ),
                "average_buy_max_drawdown_pct": (
                    0.0
                    if buy_weight <= 0
                    else round(
                        item["drawdown_weighted"] / buy_weight / 100.0,
                        2,
                    )
                ),
                "profit_factor": (
                    None
                    if item["profit_factor_weight"] <= 0
                    else round(
                        item["profit_factor_weighted"]
                        / item["profit_factor_weight"]
                        / 1000.0,
                        3,
                    )
                ),
            }
        )
    return summaries
