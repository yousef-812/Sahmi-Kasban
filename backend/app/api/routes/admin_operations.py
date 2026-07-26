from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.market_data.provider import get_market_data_provider
from app.market_data.types import MarketDataProvider
from app.schemas.operations import (
    AdminAuditEventResponse,
    AdminAuditListResponse,
    AdminBroadcastRequest,
    AdminBroadcastResponse,
    AdminOverviewResponse,
    AdminUserListItem,
    AdminUserListResponse,
    OperationalSettingResponse,
    OperationalSettingsResponse,
    OperationalSettingUpdateRequest,
    ServiceHealthListResponse,
    ServiceHealthResponse,
)
from app.services.admin_operations import (
    get_admin_overview,
    list_admin_audit_events,
    list_admin_users,
    list_latest_service_health,
    probe_service_health,
)
from app.services.community_ai import get_community_ai_service
from app.services.notifications import NotificationError, broadcast_notifications
from app.services.operations_settings import (
    OperationalSettingError,
    list_operational_settings,
    setting_definitions,
    update_operational_setting,
)
from sahmi_kasban.ai import SahmiAIService

router = APIRouter(prefix="/admin/operations", tags=["admin-operations"])
AdminMarketProvider = Annotated[
    MarketDataProvider,
    Depends(get_market_data_provider),
]
AdminAIService = Annotated[
    SahmiAIService,
    Depends(get_community_ai_service),
]


def _setting_response(definition, stored) -> OperationalSettingResponse:
    return OperationalSettingResponse(
        key=definition.key,
        category=definition.category,
        label=definition.label,
        description=definition.description,
        kind=definition.kind,
        value=definition.default_value if stored is None else stored.value,
        default_value=definition.default_value,
        min_value=definition.min_value,
        max_value=definition.max_value,
        updated_at=None if stored is None else stored.updated_at,
    )


def _health_response(item) -> ServiceHealthResponse:
    return ServiceHealthResponse(
        id=item.id,
        component=item.component,
        provider=item.provider,
        status=item.status,
        latency_ms=item.latency_ms,
        details=item.details,
        observed_at=item.observed_at,
    )


@router.get("/overview", response_model=AdminOverviewResponse)
def admin_overview(
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> AdminOverviewResponse:
    return AdminOverviewResponse(**get_admin_overview(db))


@router.get("/users", response_model=AdminUserListResponse)
def admin_users(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    q: str | None = Query(default=None, max_length=120),
    user_status: str | None = Query(default=None, max_length=24),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AdminUserListResponse:
    items, total = list_admin_users(
        db,
        query_text=q,
        status=user_status,
        limit=limit,
        offset=offset,
    )
    return AdminUserListResponse(
        items=[AdminUserListItem(**item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/settings", response_model=OperationalSettingsResponse)
def admin_settings(
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> OperationalSettingsResponse:
    return OperationalSettingsResponse(
        items=[
            _setting_response(definition, stored)
            for definition, stored in list_operational_settings(db)
        ]
    )


@router.put(
    "/settings/{setting_key}",
    response_model=OperationalSettingResponse,
)
def update_admin_setting(
    setting_key: str,
    payload: OperationalSettingUpdateRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> OperationalSettingResponse:
    try:
        stored = update_operational_setting(
            db,
            admin_user_id=admin.id,
            key=setting_key,
            value=payload.value,
        )
        db.commit()
    except OperationalSettingError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    definition = setting_definitions()[setting_key]
    return _setting_response(definition, stored)


@router.get("/audit", response_model=AdminAuditListResponse)
def admin_audit(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    action: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> AdminAuditListResponse:
    items, total = list_admin_audit_events(
        db,
        action=action,
        limit=limit,
        offset=offset,
    )
    return AdminAuditListResponse(
        items=[
            AdminAuditEventResponse(
                id=item.id,
                actor_user_id=item.actor_user_id,
                target_user_id=item.target_user_id,
                discussion_id=item.discussion_id,
                action=item.action,
                reason_code=item.reason_code,
                details=item.details,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/providers", response_model=ServiceHealthListResponse)
def provider_health(
    db: DatabaseSession,
    _admin: CurrentAdmin,
) -> ServiceHealthListResponse:
    return ServiceHealthListResponse(
        items=[_health_response(item) for item in list_latest_service_health(db)]
    )


@router.post("/providers/probe", response_model=ServiceHealthListResponse)
async def probe_providers(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    market_provider: AdminMarketProvider,
    ai_service: AdminAIService,
) -> ServiceHealthListResponse:
    items = await probe_service_health(
        db,
        market_provider=market_provider,
        ai_service=ai_service,
    )
    db.commit()
    return ServiceHealthListResponse(items=[_health_response(item) for item in items])


@router.post(
    "/notifications/broadcast",
    response_model=AdminBroadcastResponse,
)
def broadcast_admin_notification(
    payload: AdminBroadcastRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> AdminBroadcastResponse:
    try:
        result = broadcast_notifications(
            db,
            admin_user_id=admin.id,
            title=payload.title,
            body=payload.body,
            category=payload.category,
            data=payload.data,
            audience=payload.audience,
            plan_code=payload.plan_code,
            user_ids=payload.user_ids,
        )
        db.commit()
    except NotificationError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return AdminBroadcastResponse(
        targeted_users=result.targeted_users,
        notifications_created=result.notifications_created,
        push_sent=result.push_sent,
        push_failed=result.push_failed,
        push_skipped=result.push_skipped,
    )
