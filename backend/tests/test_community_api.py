from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Discussion, User
from app.services.community import apply_moderation_decision

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


def discussion_payload(submission_key: str) -> dict[str, str]:
    return {
        "submission_key": submission_key,
        "ticker": "comi",
        "title": "رؤية فنية لحركة سهم البنك التجاري",
        "content": (
            "السهم قريب من منطقة دعم مهمة وأراقب تأكيد الحركة قبل اتخاذ القرار "
            "مع الالتزام بوقف الخسارة."
        ),
        "period_type": "week",
    }


def test_community_submission_list_report_and_mute_flow(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    author_tokens = register_and_login(
        client,
        fake_email_service,
        email="api-author@example.com",
        display_name="Community Author",
    )
    viewer_tokens = register_and_login(
        client,
        fake_email_service,
        email="api-viewer@example.com",
        display_name="Community Viewer",
    )

    submitted = client.post(
        "/api/v1/community/discussions",
        headers=headers(author_tokens),
        json=discussion_payload("api-community-001"),
    )
    assert submitted.status_code == 201
    submitted_payload = submitted.json()
    assert submitted_payload["discussion"]["ticker"] == "COMI"
    assert submitted_payload["discussion"]["status"] == "pending_review"
    assert submitted_payload["held_points"] == 50
    assert submitted_payload["balance_points"] == 250
    assert submitted_payload["idempotent"] is False

    repeated = client.post(
        "/api/v1/community/discussions",
        headers=headers(author_tokens),
        json=discussion_payload("api-community-001"),
    )
    assert repeated.status_code == 201
    assert repeated.json()["idempotent"] is True
    assert repeated.json()["balance_points"] == 250

    discussion_id = submitted_payload["discussion"]["id"]
    discussion = db_session.scalar(
        select(Discussion).where(Discussion.id == discussion_id)
    )
    assert discussion is not None
    apply_moderation_decision(
        db_session,
        discussion_id=discussion.id,
        decision="accept",
        actor_type="ai",
        moderation_details={"provider": "test"},
        frozen_prediction={
            "ticker": "COMI",
            "direction": "up",
            "period_type": "week",
        },
    )
    db_session.commit()

    public_feed = client.get(
        "/api/v1/community/discussions",
        headers=headers(viewer_tokens),
    )
    assert public_feed.status_code == 200
    assert public_feed.json()["total"] == 1
    public_item = public_feed.json()["items"][0]
    assert public_item["id"] == discussion_id
    assert public_item["moderation_result"] == {}
    author_id = public_item["author"]["user_id"]

    report = client.post(
        f"/api/v1/community/discussions/{discussion_id}/reports",
        headers=headers(viewer_tokens),
        json={"reason_code": "misleading", "details": "الهدف غير واضح"},
    )
    assert report.status_code == 201
    assert report.json()["idempotent"] is False

    repeated_report = client.post(
        f"/api/v1/community/discussions/{discussion_id}/reports",
        headers=headers(viewer_tokens),
        json={"reason_code": "misleading", "details": "الهدف غير واضح"},
    )
    assert repeated_report.status_code == 201
    assert repeated_report.json()["idempotent"] is True

    mute = client.put(
        f"/api/v1/community/users/{author_id}/mute",
        headers=headers(viewer_tokens),
    )
    assert mute.status_code == 200
    assert mute.json()["muted"] is True

    muted_feed = client.get(
        "/api/v1/community/discussions",
        headers=headers(viewer_tokens),
    )
    assert muted_feed.status_code == 200
    assert muted_feed.json()["total"] == 0

    unmute = client.delete(
        f"/api/v1/community/users/{author_id}/mute",
        headers=headers(viewer_tokens),
    )
    assert unmute.status_code == 200
    assert unmute.json()["muted"] is False

    mine = client.get(
        "/api/v1/community/discussions/mine",
        headers=headers(author_tokens),
    )
    assert mine.status_code == 200
    assert mine.json()["total"] == 1
    assert mine.json()["items"][0]["status"] == "published"
    assert mine.json()["items"][0]["moderation_result"]["review"]["decision"] == "accept"


def test_static_rejection_returns_full_balance(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    tokens = register_and_login(
        client,
        fake_email_service,
        email="api-rejected@example.com",
        display_name="Rejected Author",
    )
    payload = discussion_payload("api-community-rejected-001")
    payload["content"] = (
        "هذا تحليل للسهم وللتواصل واتساب على 01012345678 من أجل توصيات خاصة."
    )

    response = client.post(
        "/api/v1/community/discussions",
        headers=headers(tokens),
        json=payload,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["discussion"]["status"] == "rejected"
    assert body["discussion"]["rejection_code"] in {
        "phone_number",
        "contact_details",
    }
    assert body["held_points"] == 0
    assert body["balance_points"] == 300

    user = db_session.scalar(
        select(User).where(User.email == "api-rejected@example.com")
    )
    assert user is not None
