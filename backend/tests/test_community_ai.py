from __future__ import annotations

import asyncio

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DiscussionModerationEvent, WalletEntry
from app.services.auth import register_user
from app.services.community import create_discussion
from app.services.community_ai import review_pending_discussion
from app.services.wallet import get_wallet_account
from sahmi_kasban.ai import AIProviderError

PASSWORD = "StrongPass123"


class ApprovingAIService:
    async def moderate_discussion(self, text: str) -> dict:
        assert "COMI" in text
        return {
            "approved": True,
            "category": "clean",
            "reason": "محتوى متعلق بالسهم ولا يتضمن مخالفة",
            "flags": [],
        }

    async def extract_prediction(self, text: str) -> dict:
        assert "week" in text
        return {
            "ticker": "WRONG",
            "direction": "up",
            "target_price": 145.56789,
            "deadline": "نهاية الأسبوع",
            "claims": ["اختراق المقاومة", "اختراق المقاومة", "تحسن الحجم"],
            "specificity": 2.5,
        }


class RejectingAIService:
    async def moderate_discussion(self, text: str) -> dict:
        del text
        return {
            "approved": False,
            "category": "off_topic",
            "reason": "المحتوى غير متعلق بتحليل السهم",
            "flags": ["off_topic"],
        }

    async def extract_prediction(self, text: str) -> dict:
        raise AssertionError("Prediction extraction must not run after rejection")


class FailingAIService:
    async def moderate_discussion(self, text: str) -> dict:
        del text
        raise AIProviderError("provider unavailable")

    async def extract_prediction(self, text: str) -> dict:
        raise AssertionError("Prediction extraction must not run after provider failure")


class UnclearPredictionAIService:
    async def moderate_discussion(self, text: str) -> dict:
        del text
        return {
            "approved": True,
            "category": "clean",
            "reason": "محتوى آمن",
            "flags": [],
        }

    async def extract_prediction(self, text: str) -> dict:
        del text
        return {
            "ticker": "COMI",
            "direction": "unknown",
            "target_price": None,
            "claims": [],
            "specificity": 0.1,
        }


def create_user(db: Session, email: str):
    user, _token = register_user(
        db,
        email=email,
        password=PASSWORD,
        display_name="AI Community User",
    )
    db.commit()
    return user


def create_pending_discussion(db: Session, *, email: str, key: str):
    user = create_user(db, email)
    result = create_discussion(
        db,
        user=user,
        submission_key=key,
        ticker="COMI",
        title="توقع فني لسهم البنك التجاري الدولي",
        content=(
            "أراقب الدعم الحالي وأتوقع تحسن الحركة خلال الأسبوع مع الالتزام "
            "بإدارة المخاطر وانتظار تأكيد الحجم."
        ),
        period_type="week",
    )
    db.commit()
    assert result.discussion.status == "pending_review"
    return user, result.discussion


def test_ai_acceptance_publishes_and_freezes_server_authoritative_prediction(
    db_session: Session,
) -> None:
    user, discussion = create_pending_discussion(
        db_session,
        email="ai-approved@example.com",
        key="ai-approved-submission",
    )

    result = asyncio.run(
        review_pending_discussion(
            db_session,
            discussion_id=discussion.id,
            ai_service=ApprovingAIService(),
        )
    )
    db_session.commit()

    assert result.ai_status == "published"
    assert result.discussion.status == "published"
    prediction = result.discussion.frozen_prediction
    assert prediction["ticker"] == "COMI"
    assert prediction["period_type"] == "week"
    assert prediction["direction"] == "up"
    assert prediction["target_price"] == 145.5679
    assert prediction["specificity"] == 1.0
    assert prediction["claims"] == ["اختراق المقاومة", "تحسن الحجم"]
    assert len(prediction["source_text_sha256"]) == 64
    assert get_wallet_account(db_session, user.id).balance_points == 250

    hold = db_session.scalar(
        select(WalletEntry).where(
            WalletEntry.transaction_id == discussion.wallet_hold_transaction_id
        )
    )
    assert hold is not None
    assert hold.status == "confirmed"


def test_ai_rejection_releases_hold_and_records_reason(db_session: Session) -> None:
    user, discussion = create_pending_discussion(
        db_session,
        email="ai-rejected@example.com",
        key="ai-rejected-submission",
    )

    result = asyncio.run(
        review_pending_discussion(
            db_session,
            discussion_id=discussion.id,
            ai_service=RejectingAIService(),
        )
    )
    db_session.commit()

    assert result.ai_status == "rejected"
    assert result.discussion.status == "rejected"
    assert result.discussion.rejection_code == "off_topic"
    assert get_wallet_account(db_session, user.id).balance_points == 300

    hold = db_session.scalar(
        select(WalletEntry).where(
            WalletEntry.transaction_id == discussion.wallet_hold_transaction_id
        )
    )
    assert hold is not None
    assert hold.status == "released"


def test_ai_provider_failure_keeps_pending_hold_and_allows_safe_retry(
    db_session: Session,
) -> None:
    user, discussion = create_pending_discussion(
        db_session,
        email="ai-failure@example.com",
        key="ai-failure-submission",
    )

    failed = asyncio.run(
        review_pending_discussion(
            db_session,
            discussion_id=discussion.id,
            ai_service=FailingAIService(),
        )
    )
    db_session.commit()

    assert failed.ai_status == "provider_failed"
    assert failed.discussion.status == "pending_review"
    assert failed.discussion.moderation_result["review_stage"] == "awaiting_ai_retry"
    assert failed.discussion.moderation_result["ai"]["attempts"] == 1
    assert get_wallet_account(db_session, user.id).balance_points == 250

    hold = db_session.scalar(
        select(WalletEntry).where(
            WalletEntry.transaction_id == discussion.wallet_hold_transaction_id
        )
    )
    assert hold is not None
    assert hold.status == "held"

    retried = asyncio.run(
        review_pending_discussion(
            db_session,
            discussion_id=discussion.id,
            ai_service=ApprovingAIService(),
        )
    )
    db_session.commit()

    assert retried.ai_status == "published"
    assert retried.discussion.status == "published"
    assert get_wallet_account(db_session, user.id).balance_points == 250

    failure_events = db_session.scalars(
        select(DiscussionModerationEvent).where(
            DiscussionModerationEvent.discussion_id == discussion.id,
            DiscussionModerationEvent.action == "ai_failed",
        )
    ).all()
    assert len(failure_events) == 1


def test_ai_approval_without_clear_prediction_rejects_and_refunds(
    db_session: Session,
) -> None:
    user, discussion = create_pending_discussion(
        db_session,
        email="ai-unclear@example.com",
        key="ai-unclear-submission",
    )

    result = asyncio.run(
        review_pending_discussion(
            db_session,
            discussion_id=discussion.id,
            ai_service=UnclearPredictionAIService(),
        )
    )
    db_session.commit()

    assert result.ai_status == "rejected"
    assert result.discussion.status == "rejected"
    assert result.discussion.rejection_code == "prediction_not_clear"
    assert get_wallet_account(db_session, user.id).balance_points == 300
