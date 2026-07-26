from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from cryptography.fernet import Fernet
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import (
    CommunityAdminEvent,
    Notification,
    NotificationDelivery,
    PushDevice,
    Subscription,
    User,
)
from app.services.operations_settings import get_bool_setting


class NotificationError(RuntimeError):
    """Base notification operation error."""


class NotificationNotFoundError(NotificationError):
    """Raised when a notification does not belong to the user."""


@dataclass(frozen=True, slots=True)
class PushDeviceRegistrationResult:
    device: PushDevice
    idempotent: bool


@dataclass(frozen=True, slots=True)
class BroadcastResult:
    targeted_users: int
    notifications_created: int
    push_sent: int
    push_failed: int
    push_skipped: int


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _token_cipher() -> Fernet:
    secret = get_settings().secret_key.encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
    return Fernet(key)


def _encrypt_token(token: str) -> str:
    return _token_cipher().encrypt(token.encode("utf-8")).decode("ascii")


def _decrypt_token(token: str) -> str:
    return _token_cipher().decrypt(token.encode("ascii")).decode("utf-8")


def register_push_device(
    db: Session,
    *,
    user_id: UUID,
    token: str,
    platform: str,
    moment: datetime | None = None,
) -> PushDeviceRegistrationResult:
    current = moment or datetime.now(UTC)
    digest = _token_hash(token)
    device = db.scalar(
        select(PushDevice).where(PushDevice.token_hash == digest).with_for_update()
    )
    if device is not None:
        idempotent = (
            device.user_id == user_id and device.platform == platform and device.enabled
        )
        device.user_id = user_id
        device.platform = platform
        device.encrypted_token = _encrypt_token(token)
        device.enabled = True
        device.last_seen_at = current
        device.last_error = None
        db.flush()
        return PushDeviceRegistrationResult(device=device, idempotent=idempotent)
    device = PushDevice(
        user_id=user_id,
        token_hash=digest,
        encrypted_token=_encrypt_token(token),
        platform=platform,
        enabled=True,
        last_seen_at=current,
    )
    db.add(device)
    db.flush()
    return PushDeviceRegistrationResult(device=device, idempotent=False)


def unregister_push_device(
    db: Session,
    *,
    user_id: UUID,
    token: str,
) -> bool:
    device = db.scalar(
        select(PushDevice)
        .where(
            PushDevice.user_id == user_id,
            PushDevice.token_hash == _token_hash(token),
        )
        .with_for_update()
    )
    if device is None or not device.enabled:
        return False
    device.enabled = False
    db.flush()
    return True


def create_notification(
    db: Session,
    *,
    user_id: UUID,
    title: str,
    body: str,
    category: str,
    data: dict | None = None,
    moment: datetime | None = None,
) -> Notification:
    current = moment or datetime.now(UTC)
    notification = Notification(
        user_id=user_id,
        title=title.strip(),
        body=body.strip(),
        category=category.strip(),
        data=data or {},
        sent_at=current,
    )
    db.add(notification)
    db.flush()
    return notification


def list_user_notifications(
    db: Session,
    *,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Notification], int, int]:
    filters = [Notification.user_id == user_id]
    total = int(db.scalar(select(func.count(Notification.id)).where(*filters)) or 0)
    unread = int(
        db.scalar(
            select(func.count(Notification.id)).where(
                *filters,
                Notification.read_at.is_(None),
            )
        )
        or 0
    )
    items = db.scalars(
        select(Notification)
        .where(*filters)
        .order_by(Notification.sent_at.desc(), Notification.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return list(items), total, unread


def mark_notification_read(
    db: Session,
    *,
    user_id: UUID,
    notification_id: UUID,
    moment: datetime | None = None,
) -> tuple[Notification, bool]:
    notification = db.scalar(
        select(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        .with_for_update()
    )
    if notification is None:
        raise NotificationNotFoundError("Notification does not exist")
    if notification.read_at is not None:
        return notification, True
    notification.read_at = moment or datetime.now(UTC)
    db.flush()
    return notification, False


def mark_all_notifications_read(
    db: Session,
    *,
    user_id: UUID,
    moment: datetime | None = None,
) -> int:
    current = moment or datetime.now(UTC)
    items = db.scalars(
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None),
        )
        .with_for_update()
    ).all()
    for item in items:
        item.read_at = current
    db.flush()
    return len(items)


class FCMPushSender:
    def __init__(self) -> None:
        self.mode = os.getenv("FCM_DELIVERY_MODE", "disabled").strip().lower()
        self.project_id = os.getenv("FCM_PROJECT_ID", "").strip()
        self.service_account_json = os.getenv(
            "FCM_SERVICE_ACCOUNT_JSON", ""
        ).strip()

    def _credentials(self):
        raw = self.service_account_json
        if not raw:
            raise NotificationError("FCM service account is not configured")
        path = Path(raw)
        if path.exists():
            info = json.loads(path.read_text(encoding="utf-8"))
        else:
            info = json.loads(raw)
        return service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/firebase.messaging"],
        )

    def send(
        self,
        *,
        token: str,
        title: str,
        body: str,
        data: dict,
    ) -> tuple[str, str | None, str | None]:
        if self.mode == "disabled":
            return "skipped", None, "push_disabled"
        if self.mode == "stub":
            message_id = "stub:" + hashlib.sha256(token.encode()).hexdigest()[:16]
            return "sent", message_id, None
        if self.mode != "live":
            return "failed", None, "invalid_fcm_mode"
        if not self.project_id:
            return "failed", None, "missing_fcm_project_id"
        try:
            session = AuthorizedSession(self._credentials())
            response = session.post(
                "https://fcm.googleapis.com/v1/projects/"
                f"{self.project_id}/messages:send",
                json={
                    "message": {
                        "token": token,
                        "notification": {"title": title, "body": body},
                        "data": {str(key): str(value) for key, value in data.items()},
                    }
                },
                timeout=20,
            )
            if response.status_code >= 400:
                return "failed", None, f"fcm_http_{response.status_code}"
            payload = response.json()
            return "sent", str(payload.get("name") or ""), None
        except Exception as exc:  # provider boundary
            return "failed", None, type(exc).__name__[:120]


def _target_users(
    db: Session,
    *,
    audience: str,
    plan_code: str | None,
    user_ids: list[UUID],
) -> list[User]:
    query = select(User).where(User.status == "active")
    if audience == "plan":
        query = query.join(
            Subscription,
            Subscription.user_id == User.id,
        ).where(
            Subscription.status == "active",
            Subscription.plan_code == plan_code,
        )
    elif audience == "user_ids":
        query = query.where(User.id.in_(user_ids))
    return list(db.scalars(query.order_by(User.id).limit(5_000)).all())


def broadcast_notifications(
    db: Session,
    *,
    admin_user_id: UUID,
    title: str,
    body: str,
    category: str,
    data: dict,
    audience: str,
    plan_code: str | None,
    user_ids: list[UUID],
    sender: FCMPushSender | None = None,
    moment: datetime | None = None,
) -> BroadcastResult:
    if not get_bool_setting(db, "notifications_enabled"):
        raise NotificationError("Notifications are disabled by operational settings")
    current = moment or datetime.now(UTC)
    targets = _target_users(
        db,
        audience=audience,
        plan_code=plan_code,
        user_ids=user_ids,
    )
    push_sender = sender or FCMPushSender()
    sent = failed = skipped = 0
    notifications_created = 0
    for user in targets:
        notification = create_notification(
            db,
            user_id=user.id,
            title=title,
            body=body,
            category=category,
            data=data,
            moment=current,
        )
        notifications_created += 1
        devices = db.scalars(
            select(PushDevice).where(
                PushDevice.user_id == user.id,
                PushDevice.enabled.is_(True),
            )
        ).all()
        for device in devices:
            status, message_id, error_code = push_sender.send(
                token=_decrypt_token(device.encrypted_token),
                title=title,
                body=body,
                data=data,
            )
            if status == "sent":
                sent += 1
                device.last_error = None
            elif status == "failed":
                failed += 1
                device.last_error = error_code
            else:
                skipped += 1
            db.add(
                NotificationDelivery(
                    notification_id=notification.id,
                    push_device_id=device.id,
                    status=status,
                    provider_message_id=message_id,
                    error_code=error_code,
                    attempted_at=current,
                )
            )
    db.add(
        CommunityAdminEvent(
            actor_user_id=admin_user_id,
            action="notification_broadcast",
            details={
                "audience": audience,
                "plan_code": plan_code,
                "targeted_users": len(targets),
                "notifications_created": notifications_created,
                "push_sent": sent,
                "push_failed": failed,
                "push_skipped": skipped,
                "category": category,
            },
        )
    )
    db.flush()
    return BroadcastResult(
        targeted_users=len(targets),
        notifications_created=notifications_created,
        push_sent=sent,
        push_failed=failed,
        push_skipped=skipped,
    )
