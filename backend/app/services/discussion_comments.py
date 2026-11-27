from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.admin import is_admin_email
from app.models import Discussion, DiscussionComment, User
from app.services.community import CommunityError, CommunityPermissionError, DiscussionNotFoundError

MAX_COMMENTS_PER_HOUR = 20
_LINK_RE = re.compile(r"(https?://|www\.|\b[a-z0-9-]+\.(com|net|org|io|me|co|app|ly)\b)", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?:\+?\d[\s-]?){9,}")
_PROFIT_RE = re.compile(r"(ضمان(?:ات)? (?:ربح|أرباح)|ربح مضمون|أرباح مضمونة|مضمون 100)")


class CommentRejectedError(CommunityError):
    """Raised when a comment breaks the community safety rules."""


class CommentRateLimitError(CommunityError):
    """Raised when a user posts too many comments in an hour."""


@dataclass(frozen=True)
class CommentView:
    comment: DiscussionComment
    author: User


def count_visible_comments(db: Session, discussion_id: UUID) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(DiscussionComment)
            .where(
                DiscussionComment.discussion_id == discussion_id,
                DiscussionComment.status == "visible",
            )
        )
        or 0
    )


def validate_comment_text(content: str) -> str:
    cleaned = content.strip()
    if not cleaned:
        raise CommentRejectedError("empty_comment")
    if _LINK_RE.search(cleaned):
        raise CommentRejectedError("external_link")
    if _PHONE_RE.search(cleaned):
        raise CommentRejectedError("contact_info")
    if _PROFIT_RE.search(cleaned):
        raise CommentRejectedError("profit_guarantee")
    return cleaned


def _get_published_discussion(db: Session, discussion_id: UUID) -> Discussion:
    discussion = db.get(Discussion, discussion_id)
    if discussion is None or discussion.status != "published":
        raise DiscussionNotFoundError("Discussion not found")
    return discussion


def list_comments(
    db: Session,
    *,
    discussion_id: UUID,
    limit: int,
    offset: int,
) -> tuple[list[CommentView], int]:
    _get_published_discussion(db, discussion_id)
    total = count_visible_comments(db, discussion_id)
    rows = db.execute(
        select(DiscussionComment, User)
        .join(User, User.id == DiscussionComment.user_id)
        .where(
            DiscussionComment.discussion_id == discussion_id,
            DiscussionComment.status == "visible",
        )
        .order_by(DiscussionComment.created_at.asc(), DiscussionComment.id.asc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [CommentView(comment=c, author=u) for c, u in rows], total


def create_comment(
    db: Session,
    *,
    user: User,
    discussion_id: UUID,
    content: str,
    parent_id: UUID | None,
) -> CommentView:
    _get_published_discussion(db, discussion_id)
    cleaned = validate_comment_text(content)

    since = datetime.now(UTC) - timedelta(hours=1)
    recent = db.scalar(
        select(func.count())
        .select_from(DiscussionComment)
        .where(DiscussionComment.user_id == user.id, DiscussionComment.created_at >= since)
    )
    if int(recent or 0) >= MAX_COMMENTS_PER_HOUR and not is_admin_email(user.email):
        raise CommentRateLimitError("Too many comments, try again later")

    if parent_id is not None:
        parent = db.get(DiscussionComment, parent_id)
        if parent is None or parent.discussion_id != discussion_id or parent.status != "visible":
            raise DiscussionNotFoundError("Parent comment not found")
        if parent.parent_id is not None:
            # Replies are one level deep: attach to the top-level comment.
            parent_id = parent.parent_id

    comment = DiscussionComment(
        discussion_id=discussion_id,
        user_id=user.id,
        parent_id=parent_id,
        content=cleaned,
        status="visible",
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommentView(comment=comment, author=user)


def delete_comment(db: Session, *, user: User, discussion_id: UUID, comment_id: UUID) -> None:
    comment = db.get(DiscussionComment, comment_id)
    if comment is None or comment.discussion_id != discussion_id:
        raise DiscussionNotFoundError("Comment not found")
    if comment.user_id != user.id and not is_admin_email(user.email):
        raise CommunityPermissionError("Not allowed to delete this comment")
    db.delete(comment)
    db.commit()
