from __future__ import annotations

from fastapi import APIRouter, Response, status
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.core.config import get_settings
from app.db.session import database_is_ready
from app.schemas.quality import (
    QualityStatusResponse,
    ReadinessCheckResponse,
    ReadinessResponse,
)
from app.services.quality_gates import build_quality_status

public_router = APIRouter(prefix="/health", tags=["health"])
admin_router = APIRouter(prefix="/admin/operations", tags=["admin-operations"])


@public_router.get("/ready", response_model=ReadinessResponse)
def readiness_check(
    response: Response,
    db: DatabaseSession,
) -> ReadinessResponse:
    settings = get_settings()
    checks: list[ReadinessCheckResponse] = []
    try:
        database_is_ready(db)
        checks.append(
            ReadinessCheckResponse(
                name="database",
                status="ready",
                detail="Database connection accepted a query.",
            )
        )
    except SQLAlchemyError:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        checks.append(
            ReadinessCheckResponse(
                name="database",
                status="unavailable",
                detail="Database connection failed.",
            )
        )

    ready = all(item.status == "ready" for item in checks)
    return ReadinessResponse(
        status="ready" if ready else "not_ready",
        service=settings.app_name,
        environment=settings.app_env.value,
        checks=checks,
    )


@admin_router.get("/quality", response_model=QualityStatusResponse)
def quality_status(
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> QualityStatusResponse:
    return QualityStatusResponse(**build_quality_status(db))
