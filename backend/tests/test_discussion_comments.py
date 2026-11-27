from __future__ import annotations

from uuid import UUID

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
            "السهم قريب من منطقة دعم مهمة وأراقب تأكيد الحركة قبل اتخاذ القرار مع الالتزام بوقف الخسارة."
        ),
        "period_type": "week",
    }




def _publish_discussion(client, db_session, tokens, key: str) -> str:
    submitted = client.post(
        "/api/v1/community/discussions",
        headers=headers(tokens),
        json=discussion_payload(key),
    )
    assert submitted.status_code == 201
    discussion_id = submitted.json()["discussion"]["id"]
    discussion = db_session.scalar(select(Discussion).where(Discussion.id == UUID(discussion_id)))
    assert discussion is not None
    apply_moderation_decision(
        db_session,
        discussion_id=discussion.id,
        decision="accept",
        actor_type="ai",
        moderation_details={"provider": "test"},
        frozen_prediction={"ticker": "COMI", "direction": "up", "period_type": "week"},
    )
    db_session.commit()
    return discussion_id


def test_discussion_comments_flow(client: TestClient, fake_email_service, db_session: Session) -> None:
    author = register_and_login(client, fake_email_service, email="c-author@example.com", display_name="Author")
    viewer = register_and_login(client, fake_email_service, email="c-viewer@example.com", display_name="Viewer")
    discussion_id = _publish_discussion(client, db_session, author, "comments-001")
    url = f"/api/v1/community/discussions/{discussion_id}/comments"

    assert client.post(url, json={"content": "تعليق"}).status_code in {401, 403}

    created = client.post(url, headers=headers(viewer), json={"content": "رأي مفيد، شكرا"})
    assert created.status_code == 201
    comment = created.json()
    assert comment["is_mine"] is True
    assert comment["author"]["display_name"] == "Viewer"

    reply = client.post(url, headers=headers(author), json={"content": "العفو", "parent_id": comment["id"]})
    assert reply.status_code == 201
    assert reply.json()["parent_id"] == comment["id"]

    bad_link = client.post(url, headers=headers(viewer), json={"content": "زوروا www.example.com"})
    assert bad_link.status_code == 422
    bad_profit = client.post(url, headers=headers(viewer), json={"content": "ربح مضمون في السهم ده"})
    assert bad_profit.status_code == 422

    listed = client.get(url)
    assert listed.status_code == 200
    assert listed.json()["total"] == 2
    assert [item["content"] for item in listed.json()["items"]] == ["رأي مفيد، شكرا", "العفو"]

    detail = client.get(f"/api/v1/community/discussions/{discussion_id}")
    assert detail.json()["comments_count"] == 2

    forbidden = client.delete(f"{url}/{comment['id']}", headers=headers(author))
    assert forbidden.status_code == 403
    deleted = client.delete(f"{url}/{comment['id']}", headers=headers(viewer))
    assert deleted.status_code == 200
    assert client.get(url).json()["total"] == 0
