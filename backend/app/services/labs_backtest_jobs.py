from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import LabsBacktestJob
from app.services.labs_daily_backtests import MAX_RANGE_DAYS

ALLOWED_EXIT_MODES = {"target_2", "highest"}


class LabsBacktestJobError(RuntimeError):
    """Base error for the queued labs backtest jobs."""


class LabsBacktestJobRangeError(LabsBacktestJobError):
    """Raised when the requested range or exit mode is unsupported."""


class LabsBacktestJobNotFoundError(LabsBacktestJobError):
    """Raised when the job does not belong to the requesting account."""


def create_labs_backtest_job(
    db: Session,
    *,
    actor_user_id: UUID,
    start_date: date,
    end_date: date,
    rank: int | None,
    exit_mode: str,
) -> LabsBacktestJob:
    if start_date > end_date:
        raise LabsBacktestJobRangeError("start_date must be on or before end_date")
    if (end_date - start_date).days > MAX_RANGE_DAYS:
        raise LabsBacktestJobRangeError(f"The backtest range is limited to {MAX_RANGE_DAYS} calendar days")
    if exit_mode not in ALLOWED_EXIT_MODES:
        raise LabsBacktestJobRangeError(f"Unsupported exit_mode: {exit_mode}")

    job = LabsBacktestJob(
        requested_by=actor_user_id,
        status="queued",
        start_date=start_date,
        end_date=end_date,
        rank=rank,
        exit_mode=exit_mode,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_labs_backtest_job(
    db: Session,
    *,
    job_id: UUID,
    actor_user_id: UUID,
) -> LabsBacktestJob:
    job = db.scalar(
        select(LabsBacktestJob).where(
            LabsBacktestJob.id == job_id,
            LabsBacktestJob.requested_by == actor_user_id,
        )
    )
    if job is None:
        raise LabsBacktestJobNotFoundError("لا يوجد اختبار مختبري بهذا المعرّف")
    return job


def delete_labs_backtest_job(
    db: Session,
    *,
    job_id: UUID,
    actor_user_id: UUID,
) -> None:
    job = get_labs_backtest_job(
        db,
        job_id=job_id,
        actor_user_id=actor_user_id,
    )
    db.delete(job)
    db.commit()


def list_labs_backtest_jobs(
    db: Session,
    *,
    actor_user_id: UUID,
    limit: int,
    offset: int,
) -> tuple[list[LabsBacktestJob], int]:
    filters = (LabsBacktestJob.requested_by == actor_user_id,)
    total = int(db.scalar(select(func.count()).select_from(LabsBacktestJob).where(*filters)) or 0)
    items = db.scalars(
        select(LabsBacktestJob)
        .where(*filters)
        .order_by(LabsBacktestJob.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return list(items), total


def claim_next_labs_job(db: Session) -> LabsBacktestJob | None:
    """Claim one queued job for the isolated replay worker (test machine)."""

    job = db.scalar(
        select(LabsBacktestJob)
        .where(LabsBacktestJob.status == "queued")
        .order_by(LabsBacktestJob.created_at.asc())
        .limit(1)
    )
    if job is None:
        return None
    job.status = "running"
    job.started_at = datetime.now(UTC)
    db.commit()
    db.refresh(job)
    return job


def recover_stale_labs_jobs(db: Session, *, stale_minutes: int = 15) -> int:
    """Requeue jobs left running by a worker that crashed mid-run."""

    cutoff = datetime.now(UTC) - timedelta(minutes=stale_minutes)
    stale = list(
        db.scalars(
            select(LabsBacktestJob).where(
                LabsBacktestJob.status == "running",
                LabsBacktestJob.started_at < cutoff,
            )
        ).all()
    )
    for job in stale:
        job.status = "queued"
        job.started_at = None
    if stale:
        db.commit()
    return len(stale)
