from __future__ import annotations

from fastapi.testclient import TestClient

PASSWORD = "StrongPass123"


def register_and_login(
    client: TestClient,
    fake_email_service,
    *,
    email: str,
    display_name: str,
) -> tuple[dict, dict]:
    registered = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "display_name": display_name,
            "avatar_key": "avatar_04",
        },
    )
    assert registered.status_code == 201
    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"token": fake_email_service.verification_tokens[email]},
    )
    assert verified.status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login.status_code == 200
    tokens = login.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    profile = client.get("/api/v1/profile/me", headers=headers)
    assert profile.status_code == 200
    return headers, profile.json()


def test_admin_operations_and_notification_inbox_flow(
    client: TestClient,
    fake_email_service,
    monkeypatch,
) -> None:
    admin_email = "phase8-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin_headers, admin_profile = register_and_login(
        client,
        fake_email_service,
        email=admin_email,
        display_name="Phase Eight Admin",
    )
    user_headers, user_profile = register_and_login(
        client,
        fake_email_service,
        email="phase8-user@example.com",
        display_name="Phase Eight User",
    )

    assert admin_profile["is_admin"] is True
    assert user_profile["is_admin"] is False

    forbidden = client.get(
        "/api/v1/admin/operations/overview",
        headers=user_headers,
    )
    assert forbidden.status_code == 403

    overview = client.get(
        "/api/v1/admin/operations/overview",
        headers=admin_headers,
    )
    assert overview.status_code == 200
    assert overview.json()["users_total"] == 2

    settings = client.get(
        "/api/v1/admin/operations/settings",
        headers=admin_headers,
    )
    assert settings.status_code == 200
    keys = {item["key"] for item in settings.json()["items"]}
    assert "analysis_cost_points" in keys
    assert "community_daily_limit" in keys

    updated = client.put(
        "/api/v1/admin/operations/settings/analysis_cost_points",
        headers=admin_headers,
        json={"value": 75},
    )
    assert updated.status_code == 200
    assert updated.json()["value"] == 75

    invalid = client.put(
        "/api/v1/admin/operations/settings/community_daily_limit",
        headers=admin_headers,
        json={"value": 0},
    )
    assert invalid.status_code == 422

    broadcast = client.post(
        "/api/v1/admin/operations/notifications/broadcast",
        headers=admin_headers,
        json={
            "title": "تنبيه إداري",
            "body": "تم تحديث إعدادات التشغيل.",
            "category": "announcement",
            "audience": "user_ids",
            "user_ids": [user_profile["id"]],
        },
    )
    assert broadcast.status_code == 200
    assert broadcast.json()["targeted_users"] == 1
    assert broadcast.json()["notifications_created"] == 1

    inbox = client.get("/api/v1/notifications", headers=user_headers)
    assert inbox.status_code == 200
    payload = inbox.json()
    assert payload["total"] == 1
    assert payload["unread_count"] == 1
    notification_id = payload["items"][0]["id"]

    first_read = client.post(
        f"/api/v1/notifications/{notification_id}/read",
        headers=user_headers,
    )
    assert first_read.status_code == 200
    assert first_read.json()["idempotent"] is False

    repeated_read = client.post(
        f"/api/v1/notifications/{notification_id}/read",
        headers=user_headers,
    )
    assert repeated_read.status_code == 200
    assert repeated_read.json()["idempotent"] is True

    audit = client.get(
        "/api/v1/admin/operations/audit",
        headers=admin_headers,
    )
    assert audit.status_code == 200
    actions = {item["action"] for item in audit.json()["items"]}
    assert "operational_setting_updated" in actions
    assert "notification_broadcast" in actions
