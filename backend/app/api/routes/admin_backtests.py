from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.market_data.provider import get_market_data_provider
from app.market_data.types import MarketDataProvider
from app.schemas.backtests import (
    AnalysisBacktestResultResponse,
    AnalysisBacktestRunListResponse,
    AnalysisBacktestRunRequest,
    AnalysisBacktestRunResponse,
    AnalysisBacktestVersionListResponse,
    AnalysisBacktestVersionSummaryResponse,
)
from app.services.analysis_backtests import (
    AnalysisBacktestConflictError,
    AnalysisBacktestExecution,
    AnalysisBacktestNotFoundError,
    analysis_backtest_version_summaries,
    execute_analysis_backtest,
    get_analysis_backtest_run,
    list_analysis_backtest_runs,
)

router = APIRouter(
    prefix="/admin/operations/backtests",
    tags=["admin-backtests"],
)
AdminMarketProvider = Annotated[
    MarketDataProvider,
    Depends(get_market_data_provider),
]


def _pct(value_bp: int) -> float:
    return round(value_bp / 100.0, 2)


def _result_response(item) -> AnalysisBacktestResultResponse:
    return AnalysisBacktestResultResponse(
        id=item.id,
        run_id=item.run_id,
        ticker=item.ticker,
        status=item.status,
        provider=item.provider,
        data_fingerprint=item.data_fingerprint,
        data_as_of=item.data_as_of,
        candle_count=item.candle_count,
        observations=item.observations,
        buy_count=item.buy_count,
        watch_count=item.watch_count,
        avoid_count=item.avoid_count,
        directional_accuracy_pct=_pct(item.directional_accuracy_bp),
        buy_hit_rate_pct=_pct(item.buy_hit_rate_bp),
        avoid_hit_rate_pct=_pct(item.avoid_hit_rate_bp),
        watch_hit_rate_pct=_pct(item.watch_hit_rate_bp),
        average_forward_return_pct=_pct(item.average_forward_return_bp),
        median_forward_return_pct=_pct(item.median_forward_return_bp),
        average_buy_return_pct=_pct(item.average_buy_return_bp),
        average_buy_max_drawdown_pct=_pct(item.average_buy_max_drawdown_bp),
        profit_factor=(
            None if item.profit_factor_milli is None else round(item.profit_factor_milli / 1000.0, 3)
        ),
        error_code=item.error_code,
        error_message=item.error_message,
        summary=item.summary,
    )


def _run_response(
    execution: AnalysisBacktestExecution,
) -> AnalysisBacktestRunResponse:
    run = execution.run
    return AnalysisBacktestRunResponse(
        id=run.id,
        request_key=run.request_key,
        engine_version=run.engine_version,
        status=run.status,
        tickers=list(run.tickers),
        period=run.period,
        interval=run.interval,
        min_train_size=run.min_train_size,
        horizon_sessions=run.horizon_sessions,
        step_sessions=run.step_sessions,
        neutral_band_pct=_pct(run.neutral_band_bp),
        total_tickers=run.total_tickers,
        completed_tickers=run.completed_tickers,
        failed_tickers=run.failed_tickers,
        requested_by=run.requested_by,
        started_at=run.started_at,
        completed_at=run.completed_at,
        details=run.details,
        idempotent=execution.idempotent,
        results=[_result_response(item) for item in execution.results],
    )


@router.post("/runs", response_model=AnalysisBacktestRunResponse)
async def create_backtest_run(
    payload: AnalysisBacktestRunRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
    market_provider: AdminMarketProvider,
) -> AnalysisBacktestRunResponse:
    try:
        execution = await execute_analysis_backtest(
            db,
            actor_user_id=admin.id,
            request_key=payload.request_key,
            tickers=payload.tickers,
            provider=market_provider,
            period=payload.period,
            interval=payload.interval,
            min_train_size=payload.min_train_size,
            horizon_sessions=payload.horizon_sessions,
            step_sessions=payload.step_sessions,
            neutral_band_pct=payload.neutral_band_pct,
        )
    except AnalysisBacktestConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return _run_response(execution)


@router.get("/runs", response_model=AnalysisBacktestRunListResponse)
def list_backtest_runs(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    run_status: str | None = Query(default=None, max_length=16),
    engine_version: str | None = Query(default=None, max_length=32),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AnalysisBacktestRunListResponse:
    items, total = list_analysis_backtest_runs(
        db,
        run_status=run_status,
        engine_version=engine_version,
        limit=limit,
        offset=offset,
    )
    responses = [_run_response(get_analysis_backtest_run(db, run_id=item.id)) for item in items]
    return AnalysisBacktestRunListResponse(
        items=responses,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/runs/{run_id}", response_model=AnalysisBacktestRunResponse)
def get_backtest_run(
    run_id: UUID,
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> AnalysisBacktestRunResponse:
    try:
        return _run_response(get_analysis_backtest_run(db, run_id=run_id))
    except AnalysisBacktestNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/versions",
    response_model=AnalysisBacktestVersionListResponse,
)
def list_backtest_versions(
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> AnalysisBacktestVersionListResponse:
    return AnalysisBacktestVersionListResponse(
        items=[
            AnalysisBacktestVersionSummaryResponse(**item) for item in analysis_backtest_version_summaries(db)
        ]
    )
