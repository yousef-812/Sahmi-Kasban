from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.models import AnalysisReplayJob, AnalysisReplayTicker
from app.schemas.replays import (
    HistoricalReplayCreateRequest,
    HistoricalReplayJobListResponse,
    HistoricalReplayJobResponse,
    HistoricalReplayTickerResponse,
)
from app.services.historical_replays import (
    HistoricalReplayConflictError,
    HistoricalReplayNotFoundError,
    build_historical_replay_csv,
    create_historical_replay_job,
    get_historical_replay_job,
    list_historical_replay_jobs,
    list_historical_replay_tickers,
)

router = APIRouter(
    prefix="/admin/operations/historical-replays",
    tags=["admin-historical-replays"],
)


def _ticker_response(item: AnalysisReplayTicker) -> HistoricalReplayTickerResponse:
    return HistoricalReplayTickerResponse(
        ticker=item.ticker,
        status=item.status,
        provider=item.provider,
        candle_count=item.candle_count,
        rows_written=item.rows_written,
        evaluated_rows=item.evaluated_rows,
        pending_rows=item.pending_rows,
        failed_rows=item.failed_rows,
        error_code=item.error_code,
        error_message=item.error_message,
    )


def _job_response(
    job: AnalysisReplayJob,
    *,
    tickers: list[AnalysisReplayTicker] | None = None,
) -> HistoricalReplayJobResponse:
    progress = (
        job.processed_tickers / job.total_tickers * 100.0
        if job.total_tickers
        else 0.0
    )
    return HistoricalReplayJobResponse(
        id=job.id,
        request_key=job.request_key,
        engine_version=job.engine_version,
        status=job.status,
        start_date=job.start_date,
        end_date=job.end_date,
        horizon_sessions=job.horizon_sessions,
        min_train_size=job.min_train_size,
        neutral_band_pct=round(job.neutral_band_bp / 100.0, 2),
        parallelism=job.parallelism,
        total_tickers=job.total_tickers,
        processed_tickers=job.processed_tickers,
        successful_tickers=job.successful_tickers,
        failed_tickers=job.failed_tickers,
        total_rows=job.total_rows,
        evaluated_rows=job.evaluated_rows,
        pending_rows=job.pending_rows,
        progress_pct=round(min(100.0, progress), 2),
        started_at=job.started_at,
        completed_at=job.completed_at,
        heartbeat_at=job.heartbeat_at,
        error_message=job.error_message,
        download_ready=job.total_rows > 0 and job.status in {"complete", "partial"},
        created_at=job.created_at,
        tickers=[_ticker_response(item) for item in (tickers or [])],
    )


@router.post(
    "/jobs",
    response_model=HistoricalReplayJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_replay_job(
    payload: HistoricalReplayCreateRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> HistoricalReplayJobResponse:
    try:
        job, _idempotent = create_historical_replay_job(
            db,
            actor_user_id=admin.id,
            request_key=payload.request_key,
            start_date=payload.start_date,
            end_date=payload.end_date,
            horizon_sessions=payload.horizon_sessions,
            min_train_size=payload.min_train_size,
            neutral_band_pct=payload.neutral_band_pct,
        )
    except HistoricalReplayConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return _job_response(job)


@router.get("/jobs", response_model=HistoricalReplayJobListResponse)
def list_replay_jobs(
    db: DatabaseSession,
    admin: CurrentAdmin,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> HistoricalReplayJobListResponse:
    items, total = list_historical_replay_jobs(
        db,
        actor_user_id=admin.id,
        limit=limit,
        offset=offset,
    )
    return HistoricalReplayJobListResponse(
        items=[_job_response(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/jobs/{job_id}", response_model=HistoricalReplayJobResponse)
def get_replay_job(
    job_id: UUID,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> HistoricalReplayJobResponse:
    try:
        job = get_historical_replay_job(
            db,
            job_id=job_id,
            actor_user_id=admin.id,
        )
    except HistoricalReplayNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return _job_response(
        job,
        tickers=list_historical_replay_tickers(db, job_id=job.id),
    )


@router.get("/jobs/{job_id}/export.csv")
def export_replay_job(
    job_id: UUID,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> Response:
    try:
        job = get_historical_replay_job(
            db,
            job_id=job_id,
            actor_user_id=admin.id,
        )
    except HistoricalReplayNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if job.total_rows <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="لا توجد نتائج قابلة للتنزيل حتى الآن",
        )
    filename = (
        f"sahmi-engine-replay-{job.start_date.isoformat()}-"
        f"{job.end_date.isoformat()}-{str(job.id)[:8]}.csv"
    )
    return Response(
        content=build_historical_replay_csv(db, job=job),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
