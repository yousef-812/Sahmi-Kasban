from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Discussion, DiscussionModerationEvent, WalletEntry
from app.services.auth import register_user
from app.services.community import (
    CommunityConflictError,
    DiscussionReportError,
    apply_moderation_decision,
    create_discussion,
    list_published_discussions,
    mute_user,
    report_discussion,
    unmute_user,
)
from app.services.wallet import get_wallet_account

PASSWORD = "StrongPass123"


def create_user(db: Session, email: str):
    user, _token = register_user(
        db,
        email=email,
        password=PASSWORD,
        display_name=email.split("@", maxsplit=1)[0],
    )
    db.commit()
    return user


def clean_payload() -> dict[str, str]:
    return {
        "submission_key": "submission-clean-001",
        "ticker": "COMI",
        "title": "توقع فني لسهم البنك التجاري الدولي",
        "content": (
            "أراقب منطقة الدعم الحالية وأتوقع تحسن الحركة خلال الفترة المحددة مع الالتزام بإدارة المخاطر."
        ),
        "period_type": "week",
    }


def test_submission_holds_points_and_is_idempotent(db_session: Session) -> None:
    user = create_user(db_session, "community-one@example.com")
    payload = clean_payload()

    first = create_discussion(db_session, user=user, **payload)
    db_session.commit()
    repeated = create_discussion(db_session, user=user, **payload)
    db_session.commit()

    assert first.discussion.id == repeated.discussion.id
    assert repeated.idempotent is True
    assert first.discussion.status == "pending_review"
    assert get_wallet_account(db_session, user.id).balance_points == 500


def test_accepting_discussion_confirms_hold_once(db_session: Session) -> None:
    user = create_user(db_session, "community-two@example.com")
    result = create_discussion(db_session, user=user, **clean_payload())

    accepted = apply_moderation_decision(
        db_session,
        discussion_id=result.discussion.id,
        decision="accept",
        actor_type="ai",
        moderation_details={"model": "stub", "safe": True},
        frozen_prediction={
            "ticker": "COMI",
            "direction": "up",
            "period_type": "week",
        },
    )
    repeated = apply_moderation_decision(
        db_session,
        discussion_id=result.discussion.id,
        decision="accept",
        actor_type="ai",
    )
    db_session.commit()

    assert accepted.id == repeated.id
    assert accepted.status == "published"
    assert accepted.published_at is not None
    assert accepted.frozen_prediction["direction"] == "up"
    assert get_wallet_account(db_session, user.id).balance_points == 500


def test_static_rejection_releases_full_hold_once(db_session: Session) -> None:
    user = create_user(db_session, "community-three@example.com")
    payload = clean_payload()
    payload["submission_key"] = "submission-rejected-001"
    payload["content"] = "هذا توقع للسهم وللتواصل واتساب على 01012345678 للحصول على توصيات أخرى."

    first = create_discussion(db_session, user=user, **payload)
    db_session.commit()
    repeated = create_discussion(db_session, user=user, **payload)
    db_session.commit()

    assert first.discussion.status == "rejected"
    assert first.discussion.rejection_code in {"phone_number", "contact_details"}
    assert repeated.idempotent is True
    assert get_wallet_account(db_session, user.id).balance_points == 500

    events = db_session.scalars(
        select(DiscussionModerationEvent).where(
            DiscussionModerationEvent.discussion_id == first.discussion.id
        )
    ).all()
    assert {event.action for event in events} == {"rules_rejected", "rejected"}


def test_submission_key_cannot_be_reused_for_other_content(
    db_session: Session,
) -> None:
    user = create_user(db_session, "community-four@example.com")
    payload = clean_payload()
    create_discussion(db_session, user=user, **payload)
    db_session.commit()

    changed = dict(payload)
    changed["content"] = "محتوى مختلف تمامًا مع الاحتفاظ بنفس مفتاح الطلب لاختبار منع التكرار الخاطئ."
    try:
        create_discussion(db_session, user=user, **changed)
    except CommunityConflictError:
        pass
    else:
        raise AssertionError("Expected a submission-key conflict")


def test_reports_and_mutes_are_idempotent(db_session: Session) -> None:
    author = create_user(db_session, "community-author@example.com")
    viewer = create_user(db_session, "community-viewer@example.com")
    payload = clean_payload()
    payload["submission_key"] = "submission-published-001"
    submission = create_discussion(db_session, user=author, **payload)
    apply_moderation_decision(
        db_session,
        discussion_id=submission.discussion.id,
        decision="accept",
        actor_type="ai",
    )
    db_session.commit()

    first_report = report_discussion(
        db_session,
        reporter=viewer,
        discussion_id=submission.discussion.id,
        reason_code="misleading",
    )
    repeated_report = report_discussion(
        db_session,
        reporter=viewer,
        discussion_id=submission.discussion.id,
        reason_code="misleading",
    )
    assert first_report.report.id == repeated_report.report.id
    assert repeated_report.idempotent is True

    try:
        report_discussion(
            db_session,
            reporter=author,
            discussion_id=submission.discussion.id,
            reason_code="other",
        )
    except DiscussionReportError:
        pass
    else:
        raise AssertionError("Expected own-discussion report rejection")

    mute = mute_user(
        db_session,
        muter_user_id=viewer.id,
        muted_user_id=author.id,
    )
    repeated_mute = mute_user(
        db_session,
        muter_user_id=viewer.id,
        muted_user_id=author.id,
    )
    assert mute.idempotent is False
    assert repeated_mute.idempotent is True

    muted_items, muted_total = list_published_discussions(
        db_session,
        viewer_user_id=viewer.id,
    )
    assert muted_items == []
    assert muted_total == 0

    unmute = unmute_user(
        db_session,
        muter_user_id=viewer.id,
        muted_user_id=author.id,
    )
    repeated_unmute = unmute_user(
        db_session,
        muter_user_id=viewer.id,
        muted_user_id=author.id,
    )
    db_session.commit()
    assert unmute.idempotent is False
    assert repeated_unmute.idempotent is True

    visible_items, visible_total = list_published_discussions(
        db_session,
        viewer_user_id=viewer.id,
    )
    assert visible_total == 1
    assert visible_items[0].discussion.id == submission.discussion.id

    stored = db_session.scalar(select(Discussion).where(Discussion.id == submission.discussion.id))
    assert stored is not None
