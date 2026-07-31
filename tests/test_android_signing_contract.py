from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_android_preview_contract() -> None:
    gradle = (ROOT / "mobile" / "android" / "app" / "build.gradle.kts").read_text()
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert 'applicationIdSuffix = ".ci"' in gradle
    assert "ciPreviewBuild" in gradle
    assert "googleServicesFile.exists() && !ciPreviewBuild" in gradle
    assert "SAHMI_CI_PREVIEW_BUILD" in workflow
