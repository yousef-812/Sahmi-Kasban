from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.schemas.performance import PerformanceDelayedListResponse
from app.services.performance_recovery import safe_list_delayed_performance_reports

router = APIRouter(
    prefix="/admin/operations/performance",
    tags=["admin-performance"],
)


@router.get(
    "/ledger-delayed",
    response_model=PerformanceDelayedListResponse,
)
def delayed_performance_ledger(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> PerformanceDelayedListResponse:
    items, total = safe_list_delayed_performance_reports(
        db,
        limit=limit,
        offset=offset,
    )
    return PerformanceDelayedListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )
