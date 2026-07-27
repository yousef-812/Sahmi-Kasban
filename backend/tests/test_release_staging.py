from __future__ import annotations

import pytest
from google.auth.credentials import AnonymousCredentials
from pydantic import ValidationError

from app.core.config import Environment, Settings
from app.services import notifications


POSTGRES_URL = "postgresql+psycopg://user:password@db.example/sahmi"
DIRECT_POSTGRES_URL = "postgresql+psycopg://user:password@direct.example/sahmi"


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
    with pytest.raises(ValidationError, match="SMTP_HOST"):
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
    credentials = AnonymousCredentials()
    requested_scopes: list[str] = []

    def fake_default(*, scopes: list[str]):
        requested_scopes.extend(scopes)
        return credentials, "detected-firebase-project"

    monkeypatch.setenv("FCM_DELIVERY_MODE", "live")
    monkeypatch.delenv("FCM_PROJECT_ID", raising=False)
    monkeypatch.delenv("FCM_SERVICE_ACCOUNT_JSON", raising=False)
    monkeypatch.setattr(notifications, "google_auth_default", fake_default)

    sender = notifications.FCMPushSender()

    assert sender._credentials() is credentials
    assert sender.project_id == "detected-firebase-project"
    assert requested_scopes == [
        "https://www.googleapis.com/auth/firebase.messaging"
    ]
