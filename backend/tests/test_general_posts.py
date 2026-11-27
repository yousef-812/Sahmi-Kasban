from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


PASSWORD = "StrongPass123"


def register_and_login(
    client: TestClient,
    fake_email_service,
    *,
    email: str,
    display_name: str,
) -> dict:
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": display_name,
            "avatar_key": "avatar_03",
        },
    )
    assert registered.status_code == 201

    verification = client.post(
        "/api/v1/auth/verify-email",
        json={"token": fake_email_service.verification_tokens[email]},
    )
    assert verification.status_code == 200

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login.status_code == 200
    return login.json()


def headers(tokens: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_general_post_requires_admin_and_is_idempotent(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    user = register_and_login(client, fake_email_service, email="gp-user@example.com", display_name="Plain")
    payload = {
        "submission_key": "general-post-0001",
        "title": "سؤال اليوم عن السوق",
        "content": "إيه أكتر حاجة بتشغلك في جلسة النهاردة؟ شاركنا رأيك.",
    }
    denied = client.post("/api/v1/admin/community/posts", headers=headers(user), json=payload)
    assert denied.status_code in {401, 403}

    admin_email = "gp-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin = register_and_login(client, fake_email_service, email=admin_email, display_name="Admin")
    created = client.post("/api/v1/admin/community/posts", headers=headers(admin), json=payload)
    assert created.status_code == 201
    body = created.json()
    assert body["post_type"] == "general"
    assert body["status"] == "published"
    assert body["author"]["is_admin"] is True

    again = client.post("/api/v1/admin/community/posts", headers=headers(admin), json=payload)
    assert again.status_code == 201
    assert again.json()["id"] == body["id"]

    feed = client.get("/api/v1/community/discussions")
    assert feed.status_code == 200
    assert any(item["id"] == body["id"] for item in feed.json()["items"])

