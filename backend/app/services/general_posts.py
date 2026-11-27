from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Discussion, User
from app.services.community import DiscussionView

GENERAL_TICKER = "GENERAL"


def create_general_post(
    db: Session,
    *,
    admin: User,
    submission_key: str,
    title: str,
    content: str,
    ticker: str | None,
) -> tuple[DiscussionView, bool]:
    """Publish an official (non-prediction) post. Idempotent on submission_key.

    Returns the view and whether it was already created before.
    """
    existing = db.scalar(
        select(Discussion).where(
            Discussion.user_id == admin.id,
            Discussion.submission_key == submission_key,
        )
    )
    if existing is not None:
        return DiscussionView(discussion=existing, author=admin), True

    now = datetime.now(UTC)
    discussion = Discussion(
        user_id=admin.id,
        ticker=ticker or GENERAL_TICKER,
        title=title,
        content=content,
        period_type="general",
        status="published",
        submission_key=submission_key,
        moderation_result={"provider": "admin_post"},
        frozen_prediction={},
        reviewed_at=now,
        published_at=now,
        post_type="general",
    )
    db.add(discussion)
    db.commit()
    db.refresh(discussion)
    return DiscussionView(discussion=discussion, author=admin), False
