from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Environment, Settings
from app.models import Notification, NotificationDelivery, PushDevice
from app.services.admin_operations import get_admin_overview
from app.services.auth import register_user
from app.services.notifications import (
    FCMPushSender,
    broadcast_notifications,
    list_user_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    register_push_device,
)
from app.services.operations_settings import (
    OperationalSettingError,
    get_int_setting,
    update_operational_setting,
)

PASSWORD = "StrongPass123"
POSTGRES_URL = "postgresql+psycopg://user:password@db.example/sahmi"
DIRECT_POSTGRES_URL = "postgresql+psycopg://user:password@direct.example/sahmi"


def create_user(db: Session, email: str):
    user, _token = register_user(
        db,
        email=email,
        password=PASSWORD,
        display_name=email.split("@", maxsplit=1)[0],
    )
    db.commit()
    return user


def test_runtime_setting_validation_and_audit(db_session: Session) -> None:
    admin = create_user(db_session, "ops-admin@example.com")
    stored = update_operational_setting(
        db_session,
        admin_user_id=admin.id,
        key="analysis_cost_points",
        value=80,
    )
    db_session.commit()
    assert stored.value == 80
    assert get_int_setting(db_session, "analysis_cost_points") == 80

    with pytest.raises(OperationalSettingError):
        update_operational_setting(
            db_session,
            admin_user_id=admin.id,
            key="analysis_cost_points",
            value=0,
        )


def test_push_registration_and_broadcast_are_durable(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FCM_DELIVERY_MODE", "stub")
    admin = create_user(db_session, "broadcast-admin@example.com")
    user = create_user(db_session, "broadcast-user@example.com")
    token = "device-token-that-is-long-enough-for-validation-12345"
    first = register_push_device(
        db_session,
        user_id=user.id,
        token=token,
        platform="android",
    )
    repeated = register_push_device(
        db_session,
        user_id=user.id,
        token=token,
        platform="android",
    )
    assert first.device.id == repeated.device.id
    assert repeated.idempotent is True

    result = broadcast_notifications(
        db_session,
        admin_user_id=admin.id,
        title="تحديث مهم",
        body="تم تحديث حدود التشغيل بنجاح.",
        category="announcement",
        data={"route": "/home"},
        audience="user_ids",
        plan_code=None,
        user_ids=[user.id],
        sender=FCMPushSender(),
        moment=datetime(2026, 7, 26, 10, tzinfo=UTC),
    )
    db_session.commit()
    assert result.targeted_users == 1
    assert result.notifications_created == 1
    assert result.push_sent == 1
    assert db_session.scalar(select(Notification)) is not None
    assert db_session.scalar(select(NotificationDelivery)) is not None
    assert db_session.scalar(select(PushDevice)).enabled is True


def test_notification_read_flow_and_overview(db_session: Session) -> None:
    admin = create_user(db_session, "overview-admin@example.com")
    user = create_user(db_session, "overview-user@example.com")
    result = broadcast_notifications(
        db_session,
        admin_user_id=admin.id,
        title="إشعار داخل التطبيق",
        body="هذه رسالة اختبارية.",
        category="test",
        data={},
        audience="user_ids",
        plan_code=None,
        user_ids=[user.id],
    )
    db_session.commit()
    assert result.notifications_created == 1

    items, total, unread = list_user_notifications(db_session, user_id=user.id)
    assert total == 1
    assert unread == 1
    item, idempotent = mark_notification_read(
        db_session,
        user_id=user.id,
        notification_id=items[0].id,
    )
    assert item.read_at is not None
    assert idempotent is False
    repeated, repeated_idempotent = mark_notification_read(
        db_session,
        user_id=user.id,
        notification_id=items[0].id,
    )
    assert repeated.id == item.id
    assert repeated_idempotent is True
    assert mark_all_notifications_read(db_session, user_id=user.id) == 0

    overview = get_admin_overview(db_session)
    assert overview["users_total"] == 2
    assert overview["notifications_today"] >= 1


def test_staging_allows_release_integrations_to_remain_disabled() -> None:
    settings = Settings(
        app_env=Environment.STAGING,
        debug=False,
        secret_key="staging-secret-key-that-is-long-enough",
        database_url=POSTGRES_URL,
    )

    assert settings.google_play_verification_mode == "disabled"
    assert settings.admob_ssv_verification_mode == "disabled"
    assert settings.smtp_host == ""
    assert settings.sentry_enabled is False


def test_production_keeps_release_integrations_strict() -> None:
    with pytest.raises(ValueError, match="SMTP_HOST"):
        Settings(
            app_env=Environment.PRODUCTION,
            debug=False,
            secret_key="production-secret-key-that-is-long-enough",
            database_url=POSTGRES_URL,
        )


def test_migrations_prefer_direct_database_url() -> None:
    settings = Settings(
        database_url=POSTGRES_URL,
        migration_database_url=DIRECT_POSTGRES_URL,
    )

    assert settings.effective_migration_database_url == DIRECT_POSTGRES_URL


def test_migrations_fall_back_to_runtime_database_url() -> None:
    settings = Settings(database_url=POSTGRES_URL)

    assert settings.effective_migration_database_url == POSTGRES_URL


def test_fcm_uses_application_default_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    credentials = object()
    requested_scopes: list[str] = []

    def fake_default(*, scopes: list[str]):
        requested_scopes.extend(scopes)
        return credentials, "detected-firebase-project"

    monkeypatch.setenv("FCM_DELIVERY_MODE", "live")
    monkeypatch.delenv("FCM_PROJECT_ID", raising=False)
    monkeypatch.delenv("FCM_SERVICE_ACCOUNT_JSON", raising=False)
    monkeypatch.setattr(
        "app.services.notifications.google_auth_default",
        fake_default,
    )

    sender = FCMPushSender()

    assert sender._credentials() is credentials
    assert sender.project_id == "detected-firebase-project"
    assert requested_scopes == ["https://www.googleapis.com/auth/firebase.messaging"]
