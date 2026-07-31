from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_CONFIG = ROOT / "mobile" / "lib" / "core" / "config" / "app_config.dart"
PRODUCTION_WORKFLOW = ROOT / ".github" / "workflows" / "production-android-release.yml"
PREP_SCRIPT = ROOT / "scripts" / "prepare_production_android_release.ps1"


def test_android_release_validates_only_android_ad_units() -> None:
    config = APP_CONFIG.read_text(encoding="utf-8")

    assert "RELEASE_PLATFORM" in config
    assert "'android' => <String>[" in config
    assert "admobAndroidBannerId" in config
    assert "admobAndroidNativeId" in config
    assert "admobAndroidInterstitialId" in config
    assert "'ios' => <String>[" in config


def test_production_workflow_declares_android_release_platform() -> None:
    workflow = PRODUCTION_WORKFLOW.read_text(encoding="utf-8")

    assert "--dart-define=RELEASE_PLATFORM=android" in workflow
    assert "build apk --release" in workflow
    assert "build appbundle --release" in workflow


def test_production_workflow_allows_release_without_sentry() -> None:
    workflow = PRODUCTION_WORKFLOW.read_text(encoding="utf-8")
    required_block = workflow.split("required=(", maxsplit=1)[1].split(")", maxsplit=1)[0]

    assert "SENTRY_MOBILE_DSN" not in required_block
    assert 'if [ -n "${SENTRY_MOBILE_DSN:-}" ]; then' in workflow
    assert "mobile crash monitoring will be disabled" in workflow


def test_release_preparation_script_keeps_stable_signing_identity() -> None:
    script = PREP_SCRIPT.read_text(encoding="utf-8")

    assert "ANDROID_KEYSTORE_BASE64" in script
    assert "ANDROID_EXPECTED_CERT_SHA256" in script
    assert "sahmi-kasban-upload.jks" in script
    assert "Do not delete the JKS" in script
    assert "-ForceRegenerate only before the first public release" in script


def test_release_preparation_script_supports_windows_powershell_51() -> None:
    script = PREP_SCRIPT.read_text(encoding="utf-8")

    assert "RandomNumberGenerator]::Fill" not in script
    assert "RandomNumberGenerator]::Create()" in script
    assert "$generator.GetBytes($bytes)" in script
    assert "$generator.Dispose()" in script


def test_release_preparation_script_treats_sentry_as_optional() -> None:
    script = PREP_SCRIPT.read_text(encoding="utf-8")
    required_block = script.split("$allRequiredSecrets = @(", maxsplit=1)[1].split(")", maxsplit=1)[0]

    assert "SENTRY_MOBILE_DSN" not in required_block
    assert "Optional SENTRY_MOBILE_DSN is not configured" in script
