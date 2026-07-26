from __future__ import annotations

import hashlib
import json
import unicodedata
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Discussion, User
from app.services.community import (
    CommunityConflictError,
    DiscussionSubmissionResult,
    create_discussion,
)
from app.services.operations_settings import get_int_setting
from app.services.wallet import get_wallet_account

SHORT_WINDOW = timedelta(minutes=15)
SHORT_WINDOW_MAX_SUBMISSIONS = 3
DAILY_WINDOW = timedelta(hours=24)
DAILY_WINDOW_MAX_SUBMISSIONS = 10


class CommunityRateLimitError(RuntimeError):
    """Raised when a user exceeds a durable discussion submission limit."""

    def __init__(self, message: str, *, retry_after_seconds: int) -> None:
        super().__init__(message)
        self.retry_after_seconds = max(1, retry_after_seconds)


def _normalized_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return " ".join(normalized.split()).casefold()


def discussion_content_fingerprint(
    *,
    ticker: str,
    title: str,
    content: str,
    period_type: str,
) -> str:
    canonical = json.dumps(
        {
            "ticker": ticker.strip().upper(),
            "title": _normalized_text(title),
            "content": _normalized_text(content),
            "period_type": period_type,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_duplicate_content(
    discussion: Discussion,
    *,
    ticker: str,
    title: str,
    content: str,
    period_type: str,
) -> None:
    expected = discussion_content_fingerprint(
        ticker=ticker,
        title=title,
        content=content,
        period_type=period_type,
    )
    if discussion.content_fingerprint != expected:
        raise CommunityConflictError(
            "Content fingerprint was already used for different discussion data"
        )


def _retry_after(
    timestamps: list[datetime],
    *,
    window: timedelta,
    current: datetime,
) -> int:
    oldest = min(timestamps)
    if oldest.tzinfo is None:
        oldest = oldest.replace(tzinfo=UTC)
    return max(1, int((oldest + window - current).total_seconds()) + 1)


def _enforce_submission_rate_limit(
    db: Session,
    *,
    user_id: UUID,
    moment: datetime,
) -> None:
    short_window = timedelta(
        minutes=get_int_setting(db, "community_short_window_minutes")
    )
    short_limit = get_int_setting(db, "community_short_window_limit")
    daily_limit = get_int_setting(db, "community_daily_limit")
    daily_start = moment - DAILY_WINDOW
    timestamps = list(
        db.scalars(
            select(Discussion.created_at)
            .where(
                Discussion.user_id == user_id,
                Discussion.created_at >= daily_start,
            )
            .order_by(Discussion.created_at)
        ).all()
    )
    short_timestamps = [
        timestamp
        for timestamp in timestamps
        if (timestamp.replace(tzinfo=UTC) if timestamp.tzinfo is None else timestamp)
        >= moment - short_window
    ]
    if len(short_timestamps) >= short_limit:
        raise CommunityRateLimitError(
            "Too many discussion submissions in a short period",
            retry_after_seconds=_retry_after(
                short_timestamps,
                window=short_window,
                current=moment,
            ),
        )
    if len(timestamps) >= daily_limit:
        raise CommunityRateLimitError(
            "Daily discussion submission limit reached",
            retry_after_seconds=_retry_after(
                timestamps,
                window=DAILY_WINDOW,
                current=moment,
            ),
        )


def create_safe_discussion(
    db: Session,
    *,
    user: User,
    submission_key: str,
    ticker: str,
    title: str,
    content: str,
    period_type: str,
    moment: datetime | None = None,
) -> DiscussionSubmissionResult:
    current = moment or datetime.now(UTC)
    normalized_ticker = ticker.strip().upper()
    normalized_title = title.strip()
    normalized_content = content.strip()

    existing_key = db.scalar(
        select(Discussion).where(
            Discussion.user_id == user.id,
            Discussion.submission_key == submission_key,
        )
    )
    if existing_key is not None:
        return create_discussion(
            db,
            user=user,
            submission_key=submission_key,
            ticker=normalized_ticker,
            title=normalized_title,
            content=normalized_content,
            period_type=period_type,
            moment=current,
        )

    fingerprint = discussion_content_fingerprint(
        ticker=normalized_ticker,
        title=normalized_title,
        content=normalized_content,
        period_type=period_type,
    )

    # The wallet row lock serializes submissions for the same user on PostgreSQL,
    # making the following count and duplicate checks concurrency-safe.
    account = get_wallet_account(db, user.id, lock=True)
    duplicate = db.scalar(
        select(Discussion).where(
            Discussion.user_id == user.id,
            Discussion.content_fingerprint == fingerprint,
        )
    )
    if duplicate is not None:
        _validate_duplicate_content(
            duplicate,
            ticker=normalized_ticker,
            title=normalized_title,
            content=normalized_content,
            period_type=period_type,
        )
        return DiscussionSubmissionResult(
            discussion=duplicate,
            author=user,
            balance_points=account.balance_points,
            idempotent=True,
        )

    _enforce_submission_rate_limit(db, user_id=user.id, moment=current)
    result = create_discussion(
        db,
        user=user,
        submission_key=submission_key,
        ticker=normalized_ticker,
        title=normalized_title,
        content=normalized_content,
        period_type=period_type,
        moment=current,
    )
    result.discussion.content_fingerprint = fingerprint
    db.flush()
    return result
