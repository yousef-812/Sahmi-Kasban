from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from sahmi_kasban.ai import AIClientConfig
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Discussion
from app.services.community_ai import (
    get_community_ai_service,
    review_pending_discussion,
)

logger = logging.getLogger(__name__)

_RETRY_AFTER = timedelta(minutes=10)
_BATCH_SIZE = 20


def ai_provider_is_configured() -> bool:
    config = AIClientConfig.from_env()
    return bool(config.open_webui_url or config.groq_api_keys)


def _retry_is_due(discussion: Discussion, moment: datetime) -> bool:
    result = discussion.moderation_result
    if not isinstance(result, dict) or result.get("review_stage") != "awaiting_ai_retry":
        return False
    ai_result = result.get("ai")
    if not isinstance(ai_result, dict):
        return True
    raw_attempted_at = ai_result.get("attempted_at")
    if not isinstance(raw_attempted_at, str) or not raw_attempted_at.strip():
        return True
    try:
        attempted_at = datetime.fromisoformat(raw_attempted_at)
    except ValueError:
        return True
    if attempted_at.tzinfo is None:
        attempted_at = attempted_at.replace(tzinfo=UTC)
    return attempted_at.astimezone(UTC) <= moment - _RETRY_AFTER


async def retry_pending_ai_reviews(
    moment: datetime | None = None,
) -> dict[str, int | str]:
    if not ai_provider_is_configured():
        return {"status": "skipped", "reviewed": 0, "published": 0, "rejected": 0}

    current = moment or datetime.now(UTC)
    reviewed = published = rejected = failed = 0
    with SessionLocal() as db:
        candidates = db.scalars(
            select(Discussion)
            .where(Discussion.status == "pending_review")
            .order_by(Discussion.created_at)
            .limit(100)
        ).all()
        due = [item for item in candidates if _retry_is_due(item, current)][:_BATCH_SIZE]
        ai_service = get_community_ai_service()
        for discussion in due:
            try:
                result = await review_pending_discussion(
                    db,
                    discussion_id=discussion.id,
                    ai_service=ai_service,
                    moment=current,
                )
                db.commit()
                reviewed += 1
                if result.ai_status == "published":
                    published += 1
                elif result.ai_status == "rejected":
                    rejected += 1
                elif result.ai_status == "provider_failed":
                    failed += 1
            except Exception:
                db.rollback()
                failed += 1
                logger.exception(
                    "Automatic AI retry failed for discussion %s",
                    discussion.id,
                )

    payload: dict[str, int | str] = {
        "status": "completed",
        "reviewed": reviewed,
        "published": published,
        "rejected": rejected,
        "failed": failed,
    }
    logger.info("Pending discussion AI retry result: %s", payload)
    return payload
