from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.auth import register_user
from app.services.community_safety import (
    CommunityRateLimitError,
    create_safe_discussion,
    discussion_content_fingerprint,
)
from app.services.wallet import get_wallet_account

PASSWORD = "StrongPass123"


def create_user(db: Session, email: str):
    user, _token = register_user(
        db,
        email=email,
        password=PASSWORD,
        display_name="Community Safety User",
    )
    db.commit()
    return user


def payload(*, key: str, suffix: str = "") -> dict[str, str]:
    return {
        "submission_key": key,
        "ticker": "COMI",
        "title": f"توقع فني لحركة سهم البنك التجاري {suffix}".strip(),
        "content": (
            "أراقب منطقة الدعم وأتوقع حركة صاعدة خلال الأسبوع مع انتظار تأكيد "
            f"أحجام التداول وإدارة المخاطر {suffix}"
        ).strip(),
        "period_type": "week",
    }


def test_content_fingerprint_normalizes_spacing_and_case() -> None:
    first = discussion_content_fingerprint(
        ticker="comi",
        title="  توقع   فني  ",
        content="حركة   صاعدة خلال الأسبوع",
        period_type="week",
    )
    second = discussion_content_fingerprint(
        ticker="COMI",
        title="توقع فني",
        content="حركة صاعدة خلال الأسبوع",
        period_type="week",
    )
    assert first == second


def test_same_content_with_new_submission_key_is_idempotent(db_session: Session) -> None:
    user = create_user(db_session, "safety-duplicate@example.com")
    first_payload = payload(key="duplicate-content-key-001")
    first = create_safe_discussion(db_session, user=user, **first_payload)
    db_session.commit()

    repeated_payload = dict(first_payload)
    repeated_payload["submission_key"] = "duplicate-content-key-002"
    repeated = create_safe_discussion(db_session, user=user, **repeated_payload)
    db_session.commit()

    assert first.discussion.id == repeated.discussion.id
    assert repeated.idempotent is True
    assert first.discussion.content_fingerprint is not None
    assert get_wallet_account(db_session, user.id).balance_points == 450


def test_short_window_rate_limit_rejects_before_extra_debit(db_session: Session) -> None:
    user = create_user(db_session, "safety-rate@example.com")
    for index in range(3):
        created = create_safe_discussion(
            db_session,
            user=user,
            **payload(
                key=f"rate-limit-key-{index:03d}",
                suffix=f"الحالة {index}",
            ),
        )
        assert created.idempotent is False
        db_session.commit()

    assert get_wallet_account(db_session, user.id).balance_points == 350

    try:
        create_safe_discussion(
            db_session,
            user=user,
            **payload(
                key="rate-limit-key-004",
                suffix="الحالة الرابعة",
            ),
        )
    except CommunityRateLimitError as exc:
        assert exc.retry_after_seconds > 0
        db_session.rollback()
    else:
        raise AssertionError("Expected a short-window community rate limit")

    assert get_wallet_account(db_session, user.id).balance_points == 350
