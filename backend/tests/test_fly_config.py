from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_fly_config_targets_neon_staging_safely() -> None:
    config = tomllib.loads((ROOT / "fly.toml").read_text(encoding="utf-8"))

    assert config["app"] == "sahmi-kasban"
    assert config["primary_region"] == "fra"
    assert config["build"]["dockerfile"] == "backend/Dockerfile"
    assert config["deploy"]["release_command"] == "python -m alembic upgrade head"

    environment = config["env"]
    assert environment["APP_ENV"] == "staging"
    assert environment["DEBUG"] == "false"
    assert environment["FCM_DELIVERY_MODE"] == "disabled"
    assert "DATABASE_URL" not in environment
    assert "MIGRATION_DATABASE_URL" not in environment
    assert "SECRET_KEY" not in environment

    http_service = config["http_service"]
    assert http_service["internal_port"] == 8080
    assert http_service["force_https"] is True
    assert http_service["auto_stop_machines"] == "stop"
    assert http_service["auto_start_machines"] is True
    assert http_service["min_machines_running"] == 0
    assert http_service["checks"][0]["path"] == "/api/v1/health/ready"

    machine = config["vm"][0]
    assert machine["size"] == "shared-cpu-1x"
    assert machine["memory"] == "512mb"
