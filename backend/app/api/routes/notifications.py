from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.operations import (
    NotificationListResponse,
    NotificationReadAllResponse,
    NotificationReadResponse,
    NotificationResponse,
    PushDeviceRegisterRequest,
    PushDeviceResponse,
    PushDeviceUnregisterRequest,
    PushDeviceUnregisterResponse,
)
from app.services.notifications import (
    NotificationNotFoundError,
    list_user_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    register_push_device,
    unregister_push_device,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _notification_response(item) -> NotificationResponse:
    return NotificationResponse(
        id=item.id,
        title=item.title,
        body=item.body,
        category=item.category,
        data=item.data,
        read_at=item.read_at,
        sent_at=item.sent_at,
    )


@router.post("/devices", response_model=PushDeviceResponse)
def register_device(
    payload: PushDeviceRegisterRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> PushDeviceResponse:
    result = register_push_device(
        db,
        user_id=current_user.id,
        token=payload.token,
        platform=payload.platform,
    )
    db.commit()
    return PushDeviceResponse(
        id=result.device.id,
        platform=result.device.platform,
        enabled=result.device.enabled,
        last_seen_at=result.device.last_seen_at,
        idempotent=result.idempotent,
    )


@router.post("/devices/unregister", response_model=PushDeviceUnregisterResponse)
def unregister_device(
    payload: PushDeviceUnregisterRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> PushDeviceUnregisterResponse:
    changed = unregister_push_device(
        db,
        user_id=current_user.id,
        token=payload.token,
    )
    db.commit()
    return PushDeviceUnregisterResponse(enabled=False, idempotent=not changed)


@router.get("", response_model=NotificationListResponse)
def notification_inbox(
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> NotificationListResponse:
    items, total, unread = list_user_notifications(
        db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return NotificationListResponse(
        items=[_notification_response(item) for item in items],
        total=total,
        unread_count=unread,
        limit=limit,
        offset=offset,
    )


@router.post("/read-all", response_model=NotificationReadAllResponse)
def read_all_notifications(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> NotificationReadAllResponse:
    updated = mark_all_notifications_read(db, user_id=current_user.id)
    db.commit()
    return NotificationReadAllResponse(updated=updated)


@router.post("/{notification_id}/read", response_model=NotificationReadResponse)
def read_notification(
    notification_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> NotificationReadResponse:
    try:
        item, idempotent = mark_notification_read(
            db,
            user_id=current_user.id,
            notification_id=notification_id,
        )
        db.commit()
    except NotificationNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return NotificationReadResponse(
        notification_id=item.id,
        read=True,
        idempotent=idempotent,
    )
