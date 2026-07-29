from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRADLE = ROOT / "mobile" / "android" / "app" / "build.gradle.kts"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
SIGNED_WORKFLOW = ROOT / ".github" / "workflows" / "signed-android-release.yml"
PACKAGE_ID = "com.sahmikasban.sahmi_kasban_mobile"


def test_ci_preview_cannot_impersonate_a_real_update() -> None:
    gradle = GRADLE.read_text(encoding="utf-8")
    ci = CI_WORKFLOW.read_text(encoding="utf-8")

    assert 'applicationIdSuffix = ".ci"' in gradle
    assert 'versionNameSuffix = "-ci"' in gradle
    assert 'google-services.json").exists() && keystorePropertiesFile.exists()' in gradle
    assert "ci-preview-not-an-update" in ci
    assert "sahmi-kasban-staging-apk-" not in ci


def test_signed_workflow_guards_package_and_certificate() -> None:
    workflow = SIGNED_WORKFLOW.read_text(encoding="utf-8")

    assert PACKAGE_ID in workflow
    assert "ANDROID_KEYSTORE_BASE64" in workflow
    assert "ANDROID_EXPECTED_CERT_SHA256" in workflow
    assert "release-metadata.txt" in workflow
    assert "sahmi-kasban-signed-update-" in workflow
