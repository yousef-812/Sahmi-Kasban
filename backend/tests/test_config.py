import pytest
from pydantic import ValidationError

from app.core.config import Environment, Settings


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
