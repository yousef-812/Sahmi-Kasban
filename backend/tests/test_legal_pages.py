from fastapi.testclient import TestClient

PUBLIC_LEGAL_PATHS = (
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


def test_delete_account_page_uses_existing_authenticated_api(
    client: TestClient,
) -> None:
    response = client.get("/delete-account")
    assert response.status_code == 200
    assert "/api/v1/auth/login" in response.text
    assert "/api/v1/profile/me" in response.text
    assert "حذف الحساب نهائيًا" in response.text


def test_root_advertises_legal_links(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["legal"] == "/legal"
    assert payload["privacy"] == "/privacy"
    assert payload["delete_account"] == "/delete-account"
