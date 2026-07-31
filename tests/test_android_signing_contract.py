from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRADLE = ROOT / "mobile" / "android" / "app" / "build.gradle.kts"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
SIGNED_WORKFLOW = ROOT / ".github" / "workflows" / "signed-android-release.yml"
PRODUCTION_WORKFLOW = (
    ROOT / ".github" / "workflows" / "production-android-release.yml"
)
PACKAGE_ID = "com.sahmikasban.sahmi_kasban_mobile"


def test_ci_preview_cannot_impersonate_a_real_update() -> None:
    gradle = GRADLE.read_text(encoding="utf-8")
    ci = CI_WORKFLOW.read_text(encoding="utf-8")

    assert 'applicationIdSuffix = ".ci"' in gradle
    assert 'versionNameSuffix = "-ci"' in gradle
    assert "ci-preview-not-an-update" in ci
    assert "sahmi-kasban-staging-apk-" not in ci


def test_firebase_is_not_coupled_to_release_signing() -> None:
    gradle = GRADLE.read_text(encoding="utf-8")

    assert 'if (googleServicesFile.exists())' in gradle
    assert 'google-services.json").exists() && keystorePropertiesFile.exists()' not in gradle


def test_production_android_build_rejects_test_integrations() -> None:
    gradle = GRADLE.read_text(encoding="utf-8")

    assert "SAHMI_PRODUCTION_BUILD" in gradle
    assert "Production Android builds require google-services.json" in gradle
    assert "Production Android builds require the protected release signing key" in gradle
    assert "must not use the Google AdMob test app ID" in gradle


def test_signed_workflow_guards_package_and_certificate() -> None:
    workflow = SIGNED_WORKFLOW.read_text(encoding="utf-8")

    assert PACKAGE_ID in workflow
    assert "ANDROID_KEYSTORE_BASE64" in workflow
    assert "ANDROID_EXPECTED_CERT_SHA256" in workflow
    assert "release-metadata.txt" in workflow
    assert "sahmi-kasban-signed-update-" in workflow


def test_production_workflow_requires_live_integrations_and_store_bundle() -> None:
    workflow = PRODUCTION_WORKFLOW.read_text(encoding="utf-8")

    assert "RELEASE_PRODUCTION" in workflow
    assert "SAHMI_PRODUCTION_BUILD" in workflow
    assert "APP_ENV=production" in workflow
    assert "PRODUCTION_API_BASE_URL" in workflow
    assert "FIREBASE_ANDROID_GOOGLE_SERVICES_JSON" in workflow
    assert "ADMOB_ANDROID_APP_ID" in workflow
    assert "ADMOB_ANDROID_BANNER_ID" in workflow
    assert "ADMOB_ANDROID_NATIVE_ID" in workflow
    assert "ADMOB_ANDROID_INTERSTITIAL_ID" in workflow
    assert "SENTRY_MOBILE_DSN" in workflow
    assert "flutter build appbundle --release" in workflow
    assert "production.aab" in workflow
    assert PACKAGE_ID in workflow
