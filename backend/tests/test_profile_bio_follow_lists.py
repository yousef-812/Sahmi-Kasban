from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Discussion,
    DiscussionModerationEvent,
    DiscussionReaction,
)

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
            "السهم قريب من منطقة دعم مهمة وأراقب تأكيد الحركة قبل اتخاذ القرار مع الالتزام بوقف الخسارة."
        ),
        "period_type": "week",
    }


def test_profile_bio_update_and_public_profile(
    client: TestClient,
    fake_email_service,
) -> None:
    tokens = register_and_login(
        client,
        fake_email_service,
        email="bio-user@example.com",
        display_name="Bio User",
    )
    auth_headers = headers(tokens)

    profile_before = client.get("/api/v1/profile/me", headers=auth_headers)
    assert profile_before.status_code == 200
    assert profile_before.json()["bio"] is None

    updated = client.patch(
        "/api/v1/profile/me",
        headers=auth_headers,
        json={"bio": "محلل متخصص في البنوك المصرية"},
    )
    assert updated.status_code == 200
    assert updated.json()["bio"] == "محلل متخصص في البنوك المصرية"

    profile_after = client.get("/api/v1/profile/me", headers=auth_headers)
    assert profile_after.status_code == 200
    assert profile_after.json()["bio"] == "محلل متخصص في البنوك المصرية"

    user_id = profile_after.json()["id"]
    public = client.get(
        f"/api/v1/community/users/{user_id}/profile",
        headers=auth_headers,
    )
    assert public.status_code == 200
    assert public.json()["bio"] == "محلل متخصص في البنوك المصرية"

    # Clearing the bio maps empty string to None
    cleared = client.patch(
        "/api/v1/profile/me",
        headers=auth_headers,
        json={"bio": "   "},
    )
    assert cleared.status_code == 200
    assert cleared.json()["bio"] is None


def test_followers_and_following_lists_with_follow_back(
    client: TestClient,
    fake_email_service,
) -> None:
    a_tokens = register_and_login(
        client,
        fake_email_service,
        email="follower-a@example.com",
        display_name="Follower A",
    )
    b_tokens = register_and_login(
        client,
        fake_email_service,
        email="target-b@example.com",
        display_name="Target B",
    )
    c_tokens = register_and_login(
        client,
        fake_email_service,
        email="follower-c@example.com",
        display_name="Follower C",
    )
    a_headers = headers(a_tokens)
    c_headers = headers(c_tokens)

    b_id = client.get("/api/v1/profile/me", headers=headers(b_tokens)).json()["id"]

    # A and C both follow B
    followed_a = client.post(
        f"/api/v1/community/users/{b_id}/follow",
        headers=a_headers,
    )
    assert followed_a.status_code == 200
    assert followed_a.json()["is_following"] is True
    assert followed_a.json()["followers_count"] == 1

    followed_c = client.post(
        f"/api/v1/community/users/{b_id}/follow",
        headers=c_headers,
    )
    assert followed_c.status_code == 200
    assert followed_c.json()["is_following"] is True
    assert followed_c.json()["followers_count"] == 2

    # A views B's followers: C appears with is_following=False -> follow back button
    followers = client.get(
        f"/api/v1/community/users/{b_id}/followers",
        headers=a_headers,
    )
    assert followers.status_code == 200
    body = followers.json()
    assert body["total"] == 2
    by_name = {item["display_name"]: item for item in body["items"]}
    assert by_name["Follower C"]["is_following"] is False
    assert by_name["Follower A"]["is_following"] is False

    # A follows back C
    c_id = client.get("/api/v1/profile/me", headers=c_headers).json()["id"]
    follow_back = client.post(
        f"/api/v1/community/users/{c_id}/follow",
        headers=a_headers,
    )
    assert follow_back.status_code == 200

    refreshed = client.get(
        f"/api/v1/community/users/{b_id}/followers",
        headers=a_headers,
    )
    refreshed_by_name = {item["display_name"]: item for item in refreshed.json()["items"]}
    assert refreshed_by_name["Follower C"]["is_following"] is True

    # Unauthenticated list also works but with no follow context
    anonymous = client.get(f"/api/v1/community/users/{b_id}/followers")
    assert anonymous.status_code == 200
    assert all(item["is_following"] is False for item in anonymous.json()["items"])

    # A's following list contains B with is_following=True
    a_id = client.get("/api/v1/profile/me", headers=a_headers).json()["id"]
    following = client.get(
        f"/api/v1/community/users/{a_id}/following",
        headers=a_headers,
    )
    assert following.status_code == 200
    following_body = following.json()
    assert following_body["total"] == 2
    following_by_name = {item["display_name"]: item for item in following_body["items"]}
    assert following_by_name["Target B"]["is_following"] is True

    missing = client.get("/api/v1/community/users/00000000-0000-0000-0000-000000000000/followers")
    assert missing.status_code == 404


def test_delete_own_discussion(
    client: TestClient,
    fake_email_service,
    db_session: Session,
) -> None:
    author_tokens = register_and_login(
        client,
        fake_email_service,
        email="delete-author@example.com",
        display_name="Delete Author",
    )
    other_tokens = register_and_login(
        client,
        fake_email_service,
        email="delete-other@example.com",
        display_name="Delete Other",
    )
    author_headers = headers(author_tokens)
    other_headers = headers(other_tokens)

    submitted = client.post(
        "/api/v1/community/discussions",
        headers=author_headers,
        json=discussion_payload("delete-discussion-001"),
    )
    assert submitted.status_code == 201
    discussion_id = submitted.json()["discussion"]["id"]
    discussion_uuid = UUID(discussion_id)

    # Other users cannot delete someone else's discussion
    forbidden = client.delete(
        f"/api/v1/community/discussions/{discussion_id}",
        headers=other_headers,
    )
    assert forbidden.status_code == 403

    # Add a reaction so we can verify cascade cleanup
    c_tokens = register_and_login(
        client,
        fake_email_service,
        email="delete-reactor@example.com",
        display_name="Delete Reactor",
    )
    reacted = client.post(
        f"/api/v1/community/discussions/{discussion_id}/reactions",
        headers=headers(c_tokens),
        json={"reaction_type": "agree"},
    )
    assert reacted.status_code == 200

    deleted = client.delete(
        f"/api/v1/community/discussions/{discussion_id}",
        headers=author_headers,
    )
    assert deleted.status_code == 200

    assert db_session.scalar(
        select(Discussion).where(Discussion.id == discussion_uuid)
    ) is None
    assert (
        db_session.scalar(
            select(func.count(DiscussionReaction.id)).where(
                DiscussionReaction.discussion_id == discussion_uuid
            )
        )
        == 0
    )
    assert (
        db_session.scalar(
            select(func.count(DiscussionModerationEvent.id)).where(
                DiscussionModerationEvent.discussion_id == discussion_uuid
            )
        )
        == 0
    )

    mine = client.get("/api/v1/community/discussions/mine", headers=author_headers)
    assert mine.status_code == 200
    assert all(item["id"] != discussion_id for item in mine.json()["items"])


def test_admin_can_delete_any_discussion(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    monkeypatch.setenv("ADMIN_EMAILS", "admin-delete@example.com")
    admin_tokens = register_and_login(
        client,
        fake_email_service,
        email="admin-delete@example.com",
        display_name="Admin Delete",
    )
    author_tokens = register_and_login(
        client,
        fake_email_service,
        email="admin-author@example.com",
        display_name="Admin Author",
    )
    admin_headers = headers(admin_tokens)

    submitted = client.post(
        "/api/v1/community/discussions",
        headers=headers(author_tokens),
        json=discussion_payload("admin-delete-discussion-001"),
    )
    assert submitted.status_code == 201
    discussion_id = submitted.json()["discussion"]["id"]

    deleted = client.delete(
        f"/api/v1/community/discussions/{discussion_id}",
        headers=admin_headers,
    )
    assert deleted.status_code == 200
    assert (
        db_session.scalar(select(Discussion).where(Discussion.id == UUID(discussion_id)))
        is None
    )