import pytest
from pydantic import ValidationError

from app.core.config import Environment, Settings


def _production_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "_env_file": None,
        "app_env": Environment.PRODUCTION,
        "database_url": "postgresql+psycopg://user:pass@db/app",
        "secret_key": "x" * 64,
        "smtp_host": "smtp.example.com",
        "google_play_verification_mode": "live",
        "google_play_service_account_json": "{}",
        "billing_token_encryption_key": "configured-by-readiness-test",
        "admob_ssv_verification_mode": "live",
        "admob_android_rewarded_ad_unit_id": (
            "ca-app-pub-1234567890123456/1234567890"
        ),
    }
    values.update(overrides)
    return Settings(**values)


def test_development_settings_allow_local_database() -> None:
    settings = Settings(
        _env_file=None,
        app_env=Environment.DEVELOPMENT,
        database_url="sqlite+pysqlite:///./test.db",
    )
    assert settings.app_env is Environment.DEVELOPMENT
    assert settings.database_url.startswith("sqlite")


def test_cors_origins_are_parsed_from_comma_separated_value() -> None:
    settings = Settings(
        _env_file=None,
        cors_origins="https://one.example, https://two.example",
    )
    assert settings.cors_origin_list == (
        "https://one.example",
        "https://two.example",
    )


def test_production_rejects_weak_secret() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(
            _env_file=None,
            app_env=Environment.PRODUCTION,
            database_url="postgresql+psycopg://user:pass@db/app",
            secret_key="too-short",
        )


def test_production_requires_postgresql() -> None:
    with pytest.raises(ValidationError, match="PostgreSQL"):
        Settings(
            _env_file=None,
            app_env=Environment.PRODUCTION,
            database_url="sqlite+pysqlite:///./production.db",
            secret_key="x" * 32,
        )


def test_android_only_production_allows_sentry_and_ios_ads_to_be_unset() -> None:
    settings = _production_settings()

    assert not settings.sentry_enabled
    assert "3940256099942544" in settings.admob_ios_rewarded_ad_unit_id


def test_production_still_rejects_android_test_rewarded_unit() -> None:
    with pytest.raises(ValidationError, match="Android AdMob test ad unit"):
        _production_settings(
            admob_android_rewarded_ad_unit_id=(
                "ca-app-pub-3940256099942544/5224354917"
            )
        )
