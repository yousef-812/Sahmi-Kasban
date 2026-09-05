from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import database_is_ready, get_db

router = APIRouter(prefix="/health", tags=["health"])
DatabaseSession = Annotated[Session, Depends(get_db)]


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str


class ReadinessCheckResponse(BaseModel):
    name: str
    status: str
    detail: str


class ReadinessHealthResponse(BaseModel):
    status: str
    database: str
    environment: str
    checks: list[ReadinessCheckResponse]


@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env.value,
    )


def _require_database(db: Session) -> None:
    try:
        database_is_ready(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc


@router.get("/ready", response_model=ReadinessHealthResponse)
def readiness_health_check(db: DatabaseSession) -> ReadinessHealthResponse:
    settings = get_settings()
    _require_database(db)
    return ReadinessHealthResponse(
        status="ready",
        database="reachable",
        environment=settings.app_env.value,
        checks=[
            ReadinessCheckResponse(
                name="database",
                status="ready",
                detail="reachable",
            )
        ],
    )


@router.get("/database", response_model=DatabaseHealthResponse)
def database_health_check(db: DatabaseSession) -> DatabaseHealthResponse:
    _require_database(db)
    return DatabaseHealthResponse(status="ok", database="reachable")


@router.get("/online_stats")
def get_online_stats(db: DatabaseSession) -> dict:
    from datetime import datetime, timedelta, UTC
    from app.models.accounts import AuthSession
    from app.models.entities import StockAnalysis, User
    from app.models.monetization import AdEventLog

    now = datetime.now(UTC)
    h1 = now - timedelta(hours=1)
    h24 = now - timedelta(hours=24)

    total_users = db.query(User).count()
    verified_users = db.query(User).filter(User.email_verified.is_(True)).count()

    active_sessions_1h = db.query(AuthSession.user_id).filter(
        AuthSession.last_seen_at >= h1, AuthSession.is_revoked.is_(False)
    ).distinct().count()

    active_sessions_24h = db.query(AuthSession.user_id).filter(
        AuthSession.last_seen_at >= h24, AuthSession.is_revoked.is_(False)
    ).distinct().count()

    ad_impressions_1h = db.query(AdEventLog).filter(
        AdEventLog.created_at >= h1, AdEventLog.event_type == 'impression'
    ).count()

    analyses_1h = db.query(StockAnalysis).filter(
        StockAnalysis.created_at >= h1
    ).count()

    return {
        "total_registered_users": total_users,
        "verified_users": verified_users,
        "active_users_last_1h": active_sessions_1h,
        "active_users_last_24h": active_sessions_24h,
        "ad_impressions_last_1h": ad_impressions_1h,
        "analyses_created_last_1h": analyses_1h,
    }
