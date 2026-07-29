from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CommunityAdminEvent, Discussion, User, WalletEntry
from app.services.community import apply_moderation_decision
from app.services.community_safety import create_safe_discussion
from app.services.wallet import get_wallet_account

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
            "avatar_key": "avatar_04",
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


def user_by_email(db: Session, email: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    assert user is not None
    return user


def create_pending(
    db: Session,
    *,
    user: User,
    key: str,
    ticker: str = "COMI",
    suffix: str = "",
) -> Discussion:
    result = create_safe_discussion(
        db,
        user=user,
        submission_key=key,
        ticker=ticker,
        title=f"توقع فني قابل للمراجعة {suffix}".strip(),
        content=(
            "أراقب الدعم الحالي وأتوقع تحسن الحركة خلال الأسبوع مع انتظار "
            f"تأكيد أحجام التداول وإدارة المخاطر {suffix}"
        ).strip(),
        period_type="week",
    )
    db.commit()
    assert result.discussion.status == "pending_review"
    return result.discussion


def test_admin_access_manual_review_hide_and_restore(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    admin_email = "community-admin@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin_tokens = register_and_login(
        client,
        fake_email_service,
        email=admin_email,
        display_name="Community Admin",
    )
    author_tokens = register_and_login(
        client,
        fake_email_service,
        email="community-author-admin-test@example.com",
        display_name="Reviewed Author",
    )
    author = user_by_email(db_session, "community-author-admin-test@example.com")
    discussion = create_pending(
        db_session,
        user=author,
        key="admin-review-pending-001",
        suffix="للقبول اليدوي",
    )

    denied = client.get(
        "/api/v1/admin/community/discussions",
        headers=headers(author_tokens),
    )
    assert denied.status_code == 403

    queue = client.get(
        "/api/v1/admin/community/discussions",
        headers=headers(admin_tokens),
    )
    assert queue.status_code == 200
    assert queue.json()["total"] == 1
    assert queue.json()["items"][0]["discussion"]["id"] == str(discussion.id)

    approved = client.post(
        f"/api/v1/admin/community/discussions/{discussion.id}/action",
        headers=headers(admin_tokens),
        json={
            "action": "approve",
            "details": "المناقشة واضحة ومتعلقة بالسهم",
            "prediction": {
                "direction": "up",
                "target_price": 145.5,
                "deadline": "نهاية الأسبوع",
                "claims": ["اختراق المقاومة"],
                "specificity": 0.8,
            },
        },
    )
    assert approved.status_code == 200
    assert approved.json()["discussion"]["status"] == "published"
    assert approved.json()["discussion"]["frozen_prediction"]["ticker"] == "COMI"
    assert approved.json()["idempotent"] is False
    assert get_wallet_account(db_session, author.id).balance_points == 950

    hold = db_session.scalar(
        select(WalletEntry).where(
            WalletEntry.transaction_id == discussion.wallet_hold_transaction_id
        )
    )
    assert hold is not None
    assert hold.status == "confirmed"

    repeated_approval = client.post(
        f"/api/v1/admin/community/discussions/{discussion.id}/action",
        headers=headers(admin_tokens),
        json={
            "action": "approve",
            "prediction": {
                "direction": "up",
                "target_price": 145.5,
                "specificity": 0.8,
            },
        },
    )
    assert repeated_approval.status_code == 200
    assert repeated_approval.json()["idempotent"] is True
    assert get_wallet_account(db_session, author.id).balance_points == 950

    hidden = client.post(
        f"/api/v1/admin/community/discussions/{discussion.id}/action",
        headers=headers(admin_tokens),
        json={
            "action": "hide",
            "reason_code": "policy_violation",
            "details": "تم الإخفاء بعد المراجعة اليدوية",
        },
    )
    assert hidden.status_code == 200
    assert hidden.json()["discussion"]["status"] == "hidden"
    assert hidden.json()["hidden_at"] is not None

    feed = client.get(
        "/api/v1/community/discussions",
        headers=headers(author_tokens),
    )
    assert feed.status_code == 200
    assert feed.json()["total"] == 0

    restored = client.post(
        f"/api/v1/admin/community/discussions/{discussion.id}/action",
        headers=headers(admin_tokens),
        json={
            "action": "restore",
            "reason_code": "appeal_reviewed",
            "details": "تمت المراجعة وتأكيد سلامة المحتوى",
        },
    )
    assert restored.status_code == 200
    assert restored.json()["discussion"]["status"] == "published"
    assert restored.json()["hidden_at"] is None

    actions = db_session.scalars(
        select(CommunityAdminEvent.action).where(
            CommunityAdminEvent.discussion_id == discussion.id
        )
    ).all()
    assert len(actions) == 3
    assert set(actions) == {
        "discussion_approve",
        "discussion_hide",
        "discussion_restore",
    }


def test_admin_block_refunds_pending_hides_published_and_revokes_old_token(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    admin_email = "block-admin@example.com"
    target_email = "blocked-community-user@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    admin_tokens = register_and_login(
        client,
        fake_email_service,
        email=admin_email,
        display_name="Block Admin",
    )
    target_tokens = register_and_login(
        client,
        fake_email_service,
        email=target_email,
        display_name="Target User",
    )
    admin = user_by_email(db_session, admin_email)
    target = user_by_email(db_session, target_email)

    published = create_pending(
        db_session,
        user=target,
        key="block-published-001",
        suffix="منشورة قبل الحظر",
    )
    apply_moderation_decision(
        db_session,
        discussion_id=published.id,
        decision="accept",
        actor_type="ai",
        frozen_prediction={
            "version": 1,
            "ticker": "COMI",
            "direction": "up",
            "period_type": "week",
        },
    )
    db_session.commit()
    pending = create_pending(
        db_session,
        user=target,
        key="block-pending-001",
        ticker="SWDY",
        suffix="معلقة وقت الحظر",
    )
    assert get_wallet_account(db_session, target.id).balance_points == 900

    self_block = client.post(
        f"/api/v1/admin/community/users/{admin.id}/block",
        headers=headers(admin_tokens),
        json={"reason_code": "invalid", "details": "لا يجوز الحظر الذاتي"},
    )
    assert self_block.status_code == 409

    blocked = client.post(
        f"/api/v1/admin/community/users/{target.id}/block",
        headers=headers(admin_tokens),
        json={
            "reason_code": "repeated_abuse",
            "details": "مخالفات متكررة بعد مراجعة البلاغات",
        },
    )
    assert blocked.status_code == 200
    body = blocked.json()
    assert body["status"] == "suspended"
    assert body["pending_rejected"] == 1
    assert body["published_hidden"] == 1
    assert body["idempotent"] is False

    db_session.refresh(target)
    db_session.refresh(published)
    db_session.refresh(pending)
    assert target.status == "suspended"
    assert published.status == "hidden"
    assert pending.status == "rejected"
    assert pending.rejection_code == "account_suspended"
    assert get_wallet_account(db_session, target.id).balance_points == 950

    old_token_access = client.get(
        "/api/v1/community/discussions/mine",
        headers=headers(target_tokens),
    )
    assert old_token_access.status_code == 401

    repeated_block = client.post(
        f"/api/v1/admin/community/users/{target.id}/block",
        headers=headers(admin_tokens),
        json={"reason_code": "repeated_abuse"},
    )
    assert repeated_block.status_code == 200
    assert repeated_block.json()["idempotent"] is True
    assert get_wallet_account(db_session, target.id).balance_points == 950

    unblocked = client.post(
        f"/api/v1/admin/community/users/{target.id}/unblock",
        headers=headers(admin_tokens),
        json={
            "reason_code": "manual_reinstatement",
            "details": "تمت إعادة تفعيل الحساب بعد المراجعة",
        },
    )
    assert unblocked.status_code == 200
    assert unblocked.json()["status"] == "active"

    still_revoked = client.get(
        "/api/v1/community/discussions/mine",
        headers=headers(target_tokens),
    )
    assert still_revoked.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": target_email, "password": PASSWORD},
    )
    assert new_login.status_code == 200
    new_access = client.get(
        "/api/v1/community/discussions/mine",
        headers=headers(new_login.json()),
    )
    assert new_access.status_code == 200

    user_actions = db_session.scalars(
        select(CommunityAdminEvent.action).where(
            CommunityAdminEvent.target_user_id == target.id,
            CommunityAdminEvent.discussion_id.is_(None),
        )
    ).all()
    assert len(user_actions) == 2
    assert set(user_actions) == {"user_blocked", "user_unblocked"}
