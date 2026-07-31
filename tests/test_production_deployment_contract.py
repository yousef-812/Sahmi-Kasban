from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING_FLY = ROOT / "fly.toml"
PRODUCTION_FLY = ROOT / "fly.production.toml"
DOCKERFILE = ROOT / "backend" / "Dockerfile"
MAIN = ROOT / "backend" / "app" / "main.py"
ANDROID_GRADLE = ROOT / "mobile" / "android" / "app" / "build.gradle.kts"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_staging_and_production_use_database_readiness_checks() -> None:
    staging = STAGING_FLY.read_text(encoding="utf-8")
    production = PRODUCTION_FLY.read_text(encoding="utf-8")

    assert 'path = "/api/v1/health/ready"' in staging
    assert 'path = "/api/v1/health/ready"' in production


def test_production_release_command_runs_preflight_before_migrations() -> None:
    production = PRODUCTION_FLY.read_text(encoding="utf-8")

    assert 'APP_ENV = "production"' in production
    assert 'FCM_DELIVERY_MODE = "live"' in production
    assert 'GOOGLE_PLAY_VERIFICATION_MODE = "live"' in production
    assert 'ADMOB_SSV_VERIFICATION_MODE = "live"' in production
    assert (
        'release_command = "python -m app.core.production_readiness && '
        'python -m alembic upgrade head"'
        in production
    )


def test_backend_container_drops_root_privileges() -> None:
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")

    assert "FROM python:3.11-slim-bookworm" in dockerfile
    assert "adduser --system" in dockerfile
    assert "USER sahmi" in dockerfile


def test_api_enforces_production_readiness_before_startup() -> None:
    main = MAIN.read_text(encoding="utf-8")

    assert "enforce_production_readiness(settings)" in main
    assert main.index("enforce_production_readiness(settings)") < main.index(
        "configure_observability(settings)"
    )


def test_android_ci_preview_is_isolated_from_release_integrations() -> None:
    gradle = ANDROID_GRADLE.read_text(encoding="utf-8")
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")

    assert 'applicationIdSuffix = ".ci"' in gradle
    assert 'versionNameSuffix = "-ci"' in gradle
    assert "ciPreviewBuild" in gradle
    assert 'SAHMI_CI_PREVIEW_BUILD: "true"' in workflow
    assert "googleServicesFile.exists() && !ciPreviewBuild" in gradle
    assert "ci-preview-not-an-update" in workflow
