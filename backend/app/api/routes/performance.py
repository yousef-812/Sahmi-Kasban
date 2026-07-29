from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.performance import (
    PerformanceReportDetailResponse,
    PerformanceReportListResponse,
    PerformanceSummaryResponse,
)
from app.services.performance_experience import (
    PerformanceExperienceError,
    PerformanceReportNotFoundError,
)
from app.services.performance_recovery import (
    safe_get_performance_report_detail,
    safe_get_performance_summary,
    safe_list_performance_reports,
)

router = APIRouter(prefix="/market/performance", tags=["market-performance"])


@router.get("/summary", response_model=PerformanceSummaryResponse)
def performance_summary(
    db: DatabaseSession,
    _current_user: CurrentUser,
    window: int = Query(default=7),
) -> PerformanceSummaryResponse:
    try:
        return PerformanceSummaryResponse(
            **safe_get_performance_summary(db, window_sessions=window)
        )
    except PerformanceExperienceError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/reports", response_model=PerformanceReportListResponse)
def performance_reports(
    db: DatabaseSession,
    _current_user: CurrentUser,
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PerformanceReportListResponse:
    items, total = safe_list_performance_reports(db, limit=limit, offset=offset)
    return PerformanceReportListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/reports/{report_id}",
    response_model=PerformanceReportDetailResponse,
)
def performance_report_detail(
    report_id: UUID,
    db: DatabaseSession,
    _current_user: CurrentUser,
) -> PerformanceReportDetailResponse:
    try:
        return PerformanceReportDetailResponse(
            **safe_get_performance_report_detail(db, report_id=report_id)
        )
    except PerformanceReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
