from __future__ import annotations

import logging
import sys

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Discussion
from app.services.community import _purge_discussion_children

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def delete_pinned_discussions() -> int:
    """Delete all currently pinned (featured) discussions from the community feed.

    This is meant to be run manually after a server deploy when legacy pinned
    discussions must be removed. Pinned discussions are automatically removed
    at startup once their session ends (`delete_ended_pinned_discussions` in
    the app lifespan); this script is the manual fallback for a full cleanup
    of every pinned discussion regardless of its session state.
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
            _purge_discussion_children(db, discussion)

        db.commit()
        logger.info("Deleted %d pinned discussion(s).", len(pinned))
        return len(pinned)


if __name__ == "__main__":
    sys.exit(delete_pinned_discussions())