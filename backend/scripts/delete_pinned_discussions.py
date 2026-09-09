from __future__ import annotations

import logging
import sys

from sqlalchemy import delete, select, update

from app.db.session import SessionLocal
from app.models import (
    AIPersonaLog,
    CommunityAdminEvent,
    Discussion,
    DiscussionAppeal,
    DiscussionImpression,
    DiscussionModerationEvent,
    DiscussionReaction,
    DiscussionReport,
    PredictionVerification,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def delete_pinned_discussions() -> int:
    """Delete all currently pinned (featured) discussions from the community feed.

    This is meant to be run manually after a server deploy when legacy pinned
    discussions must be removed. Pinned discussions are automatically unpinned
    by the scheduler when their session ends (`unpin_ended_discussions`); this
    script is the manual fallback for cleanups.
    """
    with SessionLocal() as db:
        pinned = db.scalars(
            select(Discussion).where(Discussion.is_pinned == True)  # noqa: E712
        ).all()

        if not pinned:
            logger.info("No pinned discussions found; nothing to delete.")
            return 0

        logger.info("Found %d pinned discussion(s) to delete:", len(pinned))
        for discussion in pinned:
            logger.info(
                "  - id=%s ticker=%s target_date=%s title=%s",
                discussion.id,
                discussion.ticker,
                discussion.target_date,
                discussion.title,
            )

        for discussion in pinned:
            discussion_id = discussion.id
            db.execute(
                delete(DiscussionReaction).where(
                    DiscussionReaction.discussion_id == discussion_id
                )
            )
            db.execute(
                delete(DiscussionImpression).where(
                    DiscussionImpression.discussion_id == discussion_id
                )
            )
            db.execute(
                delete(DiscussionReport).where(
                    DiscussionReport.discussion_id == discussion_id
                )
            )
            db.execute(
                delete(DiscussionModerationEvent).where(
                    DiscussionModerationEvent.discussion_id == discussion_id
                )
            )
            db.execute(
                delete(DiscussionAppeal).where(
                    DiscussionAppeal.discussion_id == discussion_id
                )
            )
            db.execute(
                delete(PredictionVerification).where(
                    PredictionVerification.discussion_id == discussion_id
                )
            )
            db.execute(
                delete(AIPersonaLog).where(AIPersonaLog.discussion_id == discussion_id)
            )
            db.execute(
                update(CommunityAdminEvent)
                .where(CommunityAdminEvent.discussion_id == discussion_id)
                .values(discussion_id=None)
            )
            db.delete(discussion)

        db.commit()
        logger.info("Deleted %d pinned discussion(s).", len(pinned))
        return len(pinned)


if __name__ == "__main__":
    sys.exit(delete_pinned_discussions())