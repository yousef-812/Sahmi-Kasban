from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.models import LabsBacktestJob
from app.schemas.labs import (
    LabsBacktestJobCreate,
    LabsBacktestJobListResponse,
    LabsBacktestJobResponse,
    LabsBacktestParams,
    LabsBacktestSession,
    LabsBacktestSummary,
)
from app.services.labs_backtest_jobs import (
    LabsBacktestJobError,
    LabsBacktestJobNotFoundError,
    LabsBacktestJobRangeError,
    create_labs_backtest_job,
    get_labs_backtest_job,
    list_labs_backtest_jobs,
)

router = APIRouter(prefix="/labs", tags=["labs"])


def _job_response(job: LabsBacktestJob) -> LabsBacktestJobResponse:
    params: LabsBacktestParams | None = None
    summary: LabsBacktestSummary | None = None
    sessions: list[LabsBacktestSession] = []
    if job.result_json:
        params = LabsBacktestParams(**job.result_json.get("params", {}))
        summary = LabsBacktestSummary(**job.result_json.get("summary", {}))
        sessions = [
            LabsBacktestSession(**item)
            for item in job.result_json.get("sessions", [])
            if isinstance(item, dict)
        ]
    return LabsBacktestJobResponse(
        id=job.id,
        status=job.status,
        start_date=job.start_date,
        end_date=job.end_date,
        rank=job.rank,
        exit_mode=job.exit_mode,
        params=params,
        summary=summary,
        sessions=sessions,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
    )


def _raise_job_error(exc: LabsBacktestJobError) -> None:
    if isinstance(exc, LabsBacktestJobNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, LabsBacktestJobRangeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=str(exc),
    ) from exc


@router.post(
    "/backtest-jobs",
    response_model=LabsBacktestJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_backtest_job(
    payload: LabsBacktestJobCreate,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> LabsBacktestJobResponse:
    try:
        job = create_labs_backtest_job(
            db,
            actor_user_id=admin.id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            rank=payload.rank,
            exit_mode=payload.exit_mode,
        )
    except LabsBacktestJobError as exc:
        _raise_job_error(exc)
    return _job_response(job)


@router.get("/backtest-jobs", response_model=LabsBacktestJobListResponse)
def list_backtest_jobs(
    db: DatabaseSession,
    admin: CurrentAdmin,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> LabsBacktestJobListResponse:
    items, total = list_labs_backtest_jobs(
        db,
        actor_user_id=admin.id,
        limit=limit,
        offset=offset,
    )
    return LabsBacktestJobListResponse(
        items=[_job_response(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/backtest-jobs/{job_id}", response_model=LabsBacktestJobResponse)
def get_backtest_job(
    job_id: UUID,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> LabsBacktestJobResponse:
    try:
        job = get_labs_backtest_job(
            db,
            job_id=job_id,
            actor_user_id=admin.id,
        )
    except LabsBacktestJobError as exc:
        _raise_job_error(exc)
    return _job_response(job)
