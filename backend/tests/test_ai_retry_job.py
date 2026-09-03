from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session, sessionmaker

from app.jobs import retry_pending_ai_reviews as retry_job
from app.models import Discussion
from app.services.auth import register_user
from app.services.community import create_discussion
from app.services.community_ai import review_pending_discussion
from app.services.wallet import get_wallet_account
from sahmi_kasban.ai import AIProviderError

PASSWORD = "StrongPass123"


class FailingAIService:
    async def moderate_discussion(self, text: str) -> dict:
        del text
        raise AIProviderError("provider unavailable")

    async def extract_prediction(self, text: str) -> dict:
        del text
        raise AssertionError("Prediction extraction must not run")


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
            "direction": "up",
            "target_price": 150.0,
            "deadline": "نهاية الأسبوع",
            "claims": ["تحسن الاتجاه"],
            "specificity": 0.8,
        }


def test_retry_job_publishes_provider_failed_discussion(
    db_session: Session,
    monkeypatch,
) -> None:
    user, _token = register_user(
        db_session,
        email="automatic-ai-retry@example.com",
        password=PASSWORD,
        display_name="Automatic Retry User",
    )
    db_session.commit()
    created = create_discussion(
        db_session,
        user=user,
        submission_key="automatic-ai-retry-submission",
        ticker="COMI",
        title="توقع فني لسهم البنك التجاري الدولي",
        content=("أتوقع تحسن اتجاه السهم خلال الأسبوع مع انتظار تأكيد الحركة والالتزام بإدارة المخاطر."),
        period_type="week",
    )
    db_session.commit()
    attempted_at = datetime(2026, 7, 28, 15, 0, tzinfo=UTC)
    failed = asyncio.run(
        review_pending_discussion(
            db_session,
            discussion_id=created.discussion.id,
            ai_service=FailingAIService(),
            moment=attempted_at,
        )
    )
    db_session.commit()
    assert failed.ai_status == "provider_failed"

    isolated_session = sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        expire_on_commit=False,
    )
    monkeypatch.setattr(retry_job, "SessionLocal", isolated_session)
    monkeypatch.setattr(retry_job, "ai_provider_is_configured", lambda: True)
    monkeypatch.setattr(
        retry_job,
        "get_community_ai_service",
        lambda: ApprovingAIService(),
    )
    result = asyncio.run(retry_job.retry_pending_ai_reviews(attempted_at + timedelta(minutes=11)))

    assert result["reviewed"] == 1
    assert result["published"] == 1
    assert result["failed"] == 0
    db_session.expire_all()
    discussion = db_session.get(Discussion, created.discussion.id)
    assert discussion is not None
    assert discussion.status == "published"
    assert discussion.moderation_result["review_stage"] == "completed"
    assert get_wallet_account(db_session, user.id).balance_points == 450
