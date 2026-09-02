from fastapi.testclient import TestClient

PUBLIC_LEGAL_PATHS = (
    "/",
    "/legal",
    "/privacy",
    "/terms",
    "/financial-disclaimer",
    "/data-safety",
    "/financial-features",
    "/delete-account",
)


def test_public_legal_pages_are_rtl_html(client: TestClient) -> None:
    for path in PUBLIC_LEGAL_PATHS:
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert 'lang="ar"' in response.text
        assert 'dir="rtl"' in response.text
        assert "سهمي كسبان" in response.text


def test_home_page_contains_navigation_buttons(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert 'href="/privacy"' in response.text
    assert 'href="/terms"' in response.text
    assert 'href="/financial-disclaimer"' in response.text
    assert 'href="/delete-account"' in response.text
    assert 'href="/app-ads.txt"' in response.text


def test_delete_account_page_uses_existing_authenticated_api(
    client: TestClient,
) -> None:
    response = client.get("/delete-account")
    assert response.status_code == 200
    assert "/api/v1/auth/login" in response.text
    assert "/api/v1/profile/me" in response.text
    assert "حذف الحساب نهائيًا" in response.text


def test_app_ads_txt_endpoint(client: TestClient) -> None:
    response = client.get("/app-ads.txt")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "google.com, pub-4624889874966809, DIRECT, f08c47fec0942fa0" in response.text
