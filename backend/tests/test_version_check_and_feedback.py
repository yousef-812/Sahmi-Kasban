from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from test_community_api import headers, register_and_login


def test_app_version_check(client: TestClient) -> None:
    res = client.get("/api/v1/app/version")
    assert res.status_code == 200
    data = res.json()
    assert data["latest_version"] == "1.0.1+28"
    assert data["latest_version_code"] == 28
    assert "com.sahmikasban.sahmi_kasban_mobile" in data["play_store_url"]


def test_user_developer_feedback_and_admin_management(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ADMIN_EMAILS", "feedback-admin@example.com")
    user_tokens = register_and_login(
        client,
        fake_email_service,
        email="feedback-user@example.com",
        display_name="Feedback Sender",
    )
    admin_tokens = register_and_login(
        client,
        fake_email_service,
        email="feedback-admin@example.com",
        display_name="Admin Reviewer",
    )

    # User submits feedback
    fb_res = client.post(
        "/api/v1/user/feedback",
        headers=headers(user_tokens),
        json={"message": "تطبيق ممتاز ولكن أرجو إضافة المزيد من المؤشرات الفنية"},
    )
    assert fb_res.status_code == 201
    fb_data = fb_res.json()
    assert fb_data["status"] == "new"
    feedback_id = fb_data["id"]

    # Admin lists feedbacks
    list_res = client.get("/api/v1/admin/feedbacks", headers=headers(admin_tokens))
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(item["id"] == feedback_id for item in list_data["items"])

    # Admin updates feedback status to reviewed
    patch_res = client.patch(
        f"/api/v1/admin/feedbacks/{feedback_id}",
        headers=headers(admin_tokens),
        json={"status": "reviewed"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "reviewed"
    assert patch_res.json()["reviewed_at"] is not None
