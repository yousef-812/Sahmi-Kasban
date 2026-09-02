from __future__ import annotations

import json

import pytest
from cryptography.fernet import Fernet

from app.core.config import Environment, Settings
from app.core.production_readiness import (
    ProductionReadinessError,
    enforce_production_readiness,
    production_readiness_issues,
)


def _service_account(project_id: str) -> str:
    return json.dumps(
        {
            "type": "service_account",
            "project_id": project_id,
            "client_email": f"service-account@{project_id}.iam.gserviceaccount.com",
            "private_key": "fixture-key-material",
        }
    )


def _production_settings() -> Settings:
    return Settings(
        _env_file=None,
        app_env=Environment.PRODUCTION,
        debug=False,
        app_public_url="https://api.sahmikasban.example",
        cors_origins="https://admin.sahmikasban.example",
        database_url="postgresql+psycopg://user:pass@db/app",
        secret_key="s" * 64,
        smtp_host="smtp.example.com",
        smtp_from_email="noreply@sahmikasban.example",
        sentry_dsn="https://public@example.ingest.sentry.io/1",
        sentry_release="sahmi-kasban-backend@test",
        google_play_verification_mode="live",
        google_play_service_account_json=_service_account("play-project"),
        billing_token_encryption_key=Fernet.generate_key().decode("ascii"),
        admob_ssv_verification_mode="live",
        admob_android_rewarded_ad_unit_id="ca-app-pub-1234567890123456/1234567890",
    )


def _production_environment() -> dict[str, str]:
    return {
        "ADMIN_EMAILS": "admin@sahmikasban.example",
        "FCM_DELIVERY_MODE": "live",
        "FCM_PROJECT_ID": "firebase-project",
        "FCM_SERVICE_ACCOUNT_JSON": _service_account("firebase-project"),
    }


def test_non_production_environment_does_not_require_live_integrations() -> None:
    settings = Settings(
        _env_file=None,
        app_env=Environment.STAGING,
        database_url="postgresql+psycopg://user:pass@db/app",
        secret_key="s" * 64,
    )

    assert production_readiness_issues(settings, {}) == ()


def test_complete_production_configuration_passes() -> None:
    settings = _production_settings()
    environment = _production_environment()

    assert production_readiness_issues(settings, environment) == ()
    enforce_production_readiness(settings, environment)


def test_production_allows_sentry_to_be_disabled() -> None:
    settings = _production_settings().model_copy(update={"sentry_dsn": "", "sentry_release": ""})

    issues = production_readiness_issues(settings, _production_environment())

    assert not any(issue.startswith("SENTRY_") for issue in issues)


def test_production_requires_release_when_sentry_is_enabled() -> None:
    settings = _production_settings().model_copy(update={"sentry_release": ""})

    issues = production_readiness_issues(settings, _production_environment())

    assert "SENTRY_RELEASE is required when SENTRY_DSN is configured" in issues


def test_production_rejects_missing_admin_and_live_push() -> None:
    settings = _production_settings()

    with pytest.raises(ProductionReadinessError) as error:
        enforce_production_readiness(settings, {})

    message = str(error.value)
    assert "ADMIN_EMAILS" in message
    assert "FCM_DELIVERY_MODE" in message
    assert "FCM_PROJECT_ID" in message
    assert "FCM_SERVICE_ACCOUNT_JSON" in message


def test_production_rejects_firebase_project_mismatch() -> None:
    settings = _production_settings()
    environment = _production_environment()
    environment["FCM_PROJECT_ID"] = "different-project"

    issues = production_readiness_issues(settings, environment)

    assert "FCM_PROJECT_ID must match the Firebase service-account project_id" in issues


def test_production_rejects_insecure_public_urls() -> None:
    settings = _production_settings().model_copy(
        update={
            "app_public_url": "http://api.example.com",
            "cors_origins": "*, http://admin.example.com",
        }
    )

    issues = production_readiness_issues(settings, _production_environment())

    assert "APP_PUBLIC_URL must be an absolute https:// URL in production" in issues
    assert "CORS_ORIGINS may contain only explicit https:// origins in production" in issues


def test_production_rejects_invalid_billing_cipher_key() -> None:
    settings = _production_settings().model_copy(update={"billing_token_encryption_key": "not-a-fernet-key"})

    issues = production_readiness_issues(settings, _production_environment())

    assert "BILLING_TOKEN_ENCRYPTION_KEY must be a valid Fernet key" in issues
