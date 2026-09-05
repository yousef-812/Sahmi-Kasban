from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Discussion,
    DiscussionImpression,
    DiscussionModerationEvent,
    DiscussionReaction,
    DiscussionReport,
    User,
    UserMute,
)
from app.services.wallet import (
    WalletHoldStateError,
    confirm_hold,
    get_wallet_account,
    hold_points,
    release_hold,
)

DISCUSSION_COST_POINTS = 0
DISCUSSION_HOLD_ENTRY_TYPE = "discussion_submission_hold"
DISCUSSION_RELEASE_ENTRY_TYPE = "discussion_submission_release"
ALLOWED_PERIOD_TYPES = {"next_session", "week", "month"}

_URL_PATTERN = re.compile(
    r"(?:https?://|www\.|(?:t\.me|wa\.me)/|(?:[a-z0-9-]+\.)+(?:com|net|org|io|me|co|eg)\b)",
    re.IGNORECASE,
)
_EGYPT_PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?20|0020|0)?1[0125](?:[\s-]?\d){8}(?!\d)")
_CONTACT_PATTERN = re.compile(
    r"(?:واتس(?:اب)?|whats?app|تليجرام|تلجرام|telegram|تواصل|اتصل|كلمني|راسلني)"
    r"\s*[:：-]?\s*@?[\w.+-]{3,}",
    re.IGNORECASE,
)
_ADVERTISEMENT_PATTERN = re.compile(
    r"(?:اشترك\s+(?:في|فى)|حم[ّ]?ل\s+التطبيق|خدمتنا|تطبيقنا|قناتنا|جروبنا|"
    r"للحجز|للتواصل|خصم\s+خاص)",
    re.IGNORECASE,
)
_GUARANTEE_PATTERN = re.compile(
    r"(?:ربح\s+مضمون|مضمون\s+100|ضمان\s+الربح|بدون\s+خسارة|"
    r"هتكسب\s+أكيد|مكسب\s+أكيد|فرصة\s+مضمونة)",
    re.IGNORECASE,
)
_ABUSE_PATTERN = re.compile(
    r"(?:يا\s+غبي|يا\s+حمار|نصاب|محتال|ابن\s+الكلب)",
    re.IGNORECASE,
)


class CommunityError(RuntimeError):
    """Base community operation error."""


class CommunityConflictError(CommunityError):
    """Raised when an idempotency key or final moderation state conflicts."""


class DiscussionNotFoundError(CommunityError):
    """Raised when a requested discussion cannot be used for the operation."""


class DiscussionReportError(CommunityError):
    """Raised when a discussion report is invalid."""


class UserMuteError(CommunityError):
    """Raised when a mute operation is invalid."""


@dataclass(frozen=True)
class DiscussionSubmissionResult:
    discussion: Discussion
    author: User
    balance_points: int
    idempotent: bool


@dataclass(frozen=True)
class DiscussionView:
    discussion: Discussion
    author: User


@dataclass(frozen=True)
class DiscussionReportResult:
    report: DiscussionReport
    idempotent: bool


@dataclass(frozen=True)
class UserMuteResult:
    muted_user_id: UUID
    muted: bool
    idempotent: bool


def _hold_transaction_id(discussion_id: UUID) -> str:
    return f"discussion:{discussion_id}:hold"


def _release_transaction_id(discussion_id: UUID) -> str:
    return f"discussion:{discussion_id}:release"


def _moderation_event(
    db: Session,
    *,
    discussion_id: UUID,
    actor_type: str,
    action: str,
    reason_code: str | None = None,
    actor_user_id: UUID | None = None,
    details: dict | None = None,
) -> DiscussionModerationEvent:
    event = DiscussionModerationEvent(
        discussion_id=discussion_id,
        actor_type=actor_type,
        actor_user_id=actor_user_id,
        action=action,
        reason_code=reason_code,
        details=details or {},
    )
    db.add(event)
    db.flush()
    return event


def static_moderation_result(title: str, content: str) -> dict:
    text = f"{title}\n{content}"
    checks = {
        "external_link": bool(_URL_PATTERN.search(text)),
        "phone_number": bool(_EGYPT_PHONE_PATTERN.search(text)),
        "contact_details": bool(_CONTACT_PATTERN.search(text)),
        "advertisement": bool(_ADVERTISEMENT_PATTERN.search(text)),
        "profit_guarantee": bool(_GUARANTEE_PATTERN.search(text)),
        "abusive_content": bool(_ABUSE_PATTERN.search(text)),
    }
    reason_codes = [code for code, matched in checks.items() if matched]
    return {
        "stage": "rules",
        "passed": not reason_codes,
        "reason_codes": reason_codes,
        "checks": checks,
    }


def _validate_existing_submission(
    discussion: Discussion,
    *,
    ticker: str,
    title: str,
    content: str,
    period_type: str,
) -> None:
    if (
        discussion.ticker != ticker
        or discussion.title != title
        or discussion.content != content
        or discussion.period_type != period_type
    ):
        raise CommunityConflictError("Submission key was already used for different discussion content")


def create_discussion(
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
    normalized_ticker = ticker.strip().upper()
    normalized_title = title.strip()
    normalized_content = content.strip()
    if period_type not in ALLOWED_PERIOD_TYPES:
        raise ValueError("Unsupported discussion period")

    existing = db.scalar(
        select(Discussion).where(
            Discussion.user_id == user.id,
            Discussion.submission_key == submission_key,
        )
    )
    if existing is not None:
        _validate_existing_submission(
            existing,
            ticker=normalized_ticker,
            title=normalized_title,
            content=normalized_content,
            period_type=period_type,
        )
        account = get_wallet_account(db, user.id)
        return DiscussionSubmissionResult(
            discussion=existing,
            author=user,
            balance_points=account.balance_points,
            idempotent=True,
        )

    discussion_id = uuid4()
    hold_transaction_id = _hold_transaction_id(discussion_id)
    discussion = Discussion(
        id=discussion_id,
        user_id=user.id,
        ticker=normalized_ticker,
        title=normalized_title,
        content=normalized_content,
        period_type=period_type,
        status="pending_review",
        submission_key=submission_key,
        wallet_hold_transaction_id=hold_transaction_id,
        moderation_result={},
        frozen_prediction={},
    )
    db.add(discussion)
    db.flush()

    if DISCUSSION_COST_POINTS > 0:
        hold_points(
            db,
            user_id=user.id,
            amount_points=DISCUSSION_COST_POINTS,
            transaction_id=hold_transaction_id,
            entry_type=DISCUSSION_HOLD_ENTRY_TYPE,
            reference_type="discussion",
            reference_id=str(discussion.id),
            details={"stage": "moderation"},
        )

    rules_result = static_moderation_result(normalized_title, normalized_content)
    discussion.moderation_result = {
        "rules": rules_result,
        "review_stage": "awaiting_ai" if rules_result["passed"] else "completed",
    }
    _moderation_event(
        db,
        discussion_id=discussion.id,
        actor_type="rules",
        action="rules_passed" if rules_result["passed"] else "rules_rejected",
        reason_code=rules_result["reason_codes"][0] if rules_result["reason_codes"] else None,
        details=rules_result,
    )

    if not rules_result["passed"]:
        apply_moderation_decision(
            db,
            discussion_id=discussion.id,
            decision="reject",
            actor_type="rules",
            reason_code=rules_result["reason_codes"][0],
            moderation_details={"rules": rules_result},
            moment=moment,
        )

    account = get_wallet_account(db, user.id)
    db.flush()
    return DiscussionSubmissionResult(
        discussion=discussion,
        author=user,
        balance_points=account.balance_points,
        idempotent=False,
    )


def apply_moderation_decision(
    db: Session,
    *,
    discussion_id: UUID,
    decision: str,
    actor_type: str,
    reason_code: str | None = None,
    actor_user_id: UUID | None = None,
    moderation_details: dict | None = None,
    frozen_prediction: dict | None = None,
    moment: datetime | None = None,
) -> Discussion:
    if decision not in {"accept", "reject"}:
        raise ValueError("Moderation decision must be accept or reject")
    if decision == "reject" and not reason_code:
        raise ValueError("Rejected discussions require a reason code")

    discussion = db.scalar(select(Discussion).where(Discussion.id == discussion_id).with_for_update())
    if discussion is None:
        raise DiscussionNotFoundError("Discussion does not exist")

    final_status = "published" if decision == "accept" else "rejected"
    if discussion.status == final_status:
        return discussion
    if discussion.status in {"published", "rejected", "hidden"}:
        raise CommunityConflictError("Discussion already has a different final moderation state")
    if discussion.status != "pending_review":
        raise CommunityConflictError("Discussion is not awaiting moderation")
    if not discussion.wallet_hold_transaction_id:
        raise WalletHoldStateError("Discussion is missing its wallet hold")

    reviewed_at = moment or datetime.now(UTC)
    current_result = dict(discussion.moderation_result)
    current_result["review"] = {
        "actor_type": actor_type,
        "decision": decision,
        "reason_code": reason_code,
        "details": moderation_details or {},
        "reviewed_at": reviewed_at.isoformat(),
    }
    current_result["review_stage"] = "completed"
    discussion.moderation_result = current_result
    discussion.reviewed_at = reviewed_at

    if decision == "accept":
        if DISCUSSION_COST_POINTS > 0:
            confirm_hold(
                db,
                user_id=discussion.user_id,
                amount_points=DISCUSSION_COST_POINTS,
                transaction_id=discussion.wallet_hold_transaction_id,
                entry_type=DISCUSSION_HOLD_ENTRY_TYPE,
                moment=reviewed_at,
            )
        discussion.status = "published"
        discussion.published_at = reviewed_at
        discussion.rejection_code = None
        discussion.frozen_prediction = frozen_prediction or {}
        action = "published"
    else:
        if DISCUSSION_COST_POINTS > 0:
            release_hold(
                db,
                user_id=discussion.user_id,
                amount_points=DISCUSSION_COST_POINTS,
                transaction_id=discussion.wallet_hold_transaction_id,
                entry_type=DISCUSSION_HOLD_ENTRY_TYPE,
                release_transaction_id=_release_transaction_id(discussion.id),
                release_entry_type=DISCUSSION_RELEASE_ENTRY_TYPE,
                reference_type="discussion",
                reference_id=str(discussion.id),
                details={"reason_code": reason_code},
            )
        discussion.status = "rejected"
        discussion.rejection_code = reason_code
        action = "rejected"

    _moderation_event(
        db,
        discussion_id=discussion.id,
        actor_type=actor_type,
        actor_user_id=actor_user_id,
        action=action,
        reason_code=reason_code,
        details=moderation_details,
    )
    db.flush()
    return discussion


def get_discussion_view(db: Session, discussion_id: UUID) -> DiscussionView:
    row = db.execute(
        select(Discussion, User)
        .join(User, User.id == Discussion.user_id)
        .where(Discussion.id == discussion_id)
    ).one_or_none()
    if row is None:
        raise DiscussionNotFoundError("Discussion does not exist")
    return DiscussionView(discussion=row[0], author=row[1])


def list_published_discussions(
    db: Session,
    *,
    viewer_user_id: UUID | None = None,
    ticker: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[DiscussionView], int]:
    filters = [Discussion.status == "published"]
    if viewer_user_id is not None:
        muted_user_ids = select(UserMute.muted_user_id).where(UserMute.muter_user_id == viewer_user_id)
        filters.append(Discussion.user_id.not_in(muted_user_ids))
    if ticker:
        filters.append(Discussion.ticker == ticker.strip().upper())

    total = db.scalar(select(func.count(Discussion.id)).where(*filters)) or 0
    rows = db.execute(
        select(Discussion, User)
        .join(User, User.id == Discussion.user_id)
        .where(*filters)
        .order_by(Discussion.published_at.desc(), Discussion.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [DiscussionView(discussion=row[0], author=row[1]) for row in rows], total


def list_user_discussions(
    db: Session,
    *,
    user: User,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[DiscussionView], int]:
    total = db.scalar(select(func.count(Discussion.id)).where(Discussion.user_id == user.id)) or 0
    discussions = db.scalars(
        select(Discussion)
        .where(Discussion.user_id == user.id)
        .order_by(Discussion.created_at.desc(), Discussion.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [DiscussionView(discussion=item, author=user) for item in discussions], total


def report_discussion(
    db: Session,
    *,
    reporter: User,
    discussion_id: UUID,
    reason_code: str,
    details: str = "",
) -> DiscussionReportResult:
    discussion = db.get(Discussion, discussion_id)
    if discussion is None or discussion.status != "published":
        raise DiscussionNotFoundError("Published discussion does not exist")
    if discussion.user_id == reporter.id:
        raise DiscussionReportError("Users cannot report their own discussion")

    existing = db.scalar(
        select(DiscussionReport).where(
            DiscussionReport.discussion_id == discussion_id,
            DiscussionReport.reporter_id == reporter.id,
        )
    )
    if existing is not None:
        return DiscussionReportResult(report=existing, idempotent=True)

    report = DiscussionReport(
        discussion_id=discussion_id,
        reporter_id=reporter.id,
        reason_code=reason_code,
        details=details.strip(),
        status="open",
        resolution_details={},
    )
    db.add(report)
    _moderation_event(
        db,
        discussion_id=discussion_id,
        actor_type="user",
        actor_user_id=reporter.id,
        action="reported",
        reason_code=reason_code,
        details={"report_details": details.strip()},
    )
    db.flush()
    return DiscussionReportResult(report=report, idempotent=False)


def mute_user(
    db: Session,
    *,
    muter_user_id: UUID,
    muted_user_id: UUID,
) -> UserMuteResult:
    if muter_user_id == muted_user_id:
        raise UserMuteError("Users cannot mute themselves")
    target = db.get(User, muted_user_id)
    if target is None or target.status != "active":
        raise UserMuteError("User to mute does not exist")

    existing = db.scalar(
        select(UserMute).where(
            UserMute.muter_user_id == muter_user_id,
            UserMute.muted_user_id == muted_user_id,
        )
    )
    if existing is not None:
        return UserMuteResult(
            muted_user_id=muted_user_id,
            muted=True,
            idempotent=True,
        )

    db.add(
        UserMute(
            muter_user_id=muter_user_id,
            muted_user_id=muted_user_id,
        )
    )
    db.flush()
    return UserMuteResult(
        muted_user_id=muted_user_id,
        muted=True,
        idempotent=False,
    )


def unmute_user(
    db: Session,
    *,
    muter_user_id: UUID,
    muted_user_id: UUID,
) -> UserMuteResult:
    existing = db.scalar(
        select(UserMute).where(
            UserMute.muter_user_id == muter_user_id,
            UserMute.muted_user_id == muted_user_id,
        )
    )
    if existing is None:
        return UserMuteResult(
            muted_user_id=muted_user_id,
            muted=False,
            idempotent=True,
        )

    db.delete(existing)
    db.flush()
    return UserMuteResult(
        muted_user_id=muted_user_id,
        muted=False,
        idempotent=False,
    )


def register_discussion_views(
    db: Session,
    discussion_ids: list[UUID],
    viewer_user_id: UUID | None = None,
) -> dict[str, int]:
    updated_counts: dict[str, int] = {}
    if not discussion_ids:
        return updated_counts

    unique_ids = list(dict.fromkeys(discussion_ids))
    for disc_id in unique_ids:
        discussion = db.get(Discussion, disc_id)
        if discussion is None or discussion.status != "published":
            continue

        if viewer_user_id is not None:
            existing = db.scalar(
                select(DiscussionImpression).where(
                    DiscussionImpression.discussion_id == disc_id,
                    DiscussionImpression.user_id == viewer_user_id,
                )
            )
            if existing is None:
                impression = DiscussionImpression(
                    user_id=viewer_user_id,
                    discussion_id=disc_id,
                )
                db.add(impression)
                discussion.views_count += 1
                db.flush()
        else:
            discussion.views_count += 1
            db.flush()

        updated_counts[str(disc_id)] = discussion.views_count

    db.commit()
    return updated_counts


def increment_discussion_view(
    db: Session,
    discussion_id: UUID,
    viewer_user_id: UUID | None = None,
) -> int:
    results = register_discussion_views(db, [discussion_id], viewer_user_id=viewer_user_id)
    return results.get(str(discussion_id), 0)


def get_discussion_reaction_counts(
    db: Session,
    discussion_id: UUID,
    user_id: UUID | None = None,
) -> tuple[int, int, str | None]:
    agree_count = int(
        db.scalar(
            select(func.count(DiscussionReaction.id)).where(
                DiscussionReaction.discussion_id == discussion_id,
                DiscussionReaction.reaction_type == "agree",
            )
        )
        or 0
    )
    disagree_count = int(
        db.scalar(
            select(func.count(DiscussionReaction.id)).where(
                DiscussionReaction.discussion_id == discussion_id,
                DiscussionReaction.reaction_type == "disagree",
            )
        )
        or 0
    )
    user_reaction: str | None = None
    if user_id is not None:
        reaction = db.scalar(
            select(DiscussionReaction).where(
                DiscussionReaction.discussion_id == discussion_id,
                DiscussionReaction.user_id == user_id,
            )
        )
        if reaction is not None:
            user_reaction = reaction.reaction_type
    return agree_count, disagree_count, user_reaction


def toggle_discussion_reaction(
    db: Session,
    *,
    user_id: UUID,
    discussion_id: UUID,
    reaction_type: str,
) -> tuple[int, int, str | None]:
    if reaction_type not in {"agree", "disagree"}:
        raise ValueError("Invalid reaction type")

    discussion = db.get(Discussion, discussion_id)
    if discussion is None:
        raise DiscussionNotFoundError("Discussion not found")

    existing = db.scalar(
        select(DiscussionReaction).where(
            DiscussionReaction.discussion_id == discussion_id,
            DiscussionReaction.user_id == user_id,
        )
    )
    if existing is not None:
        if existing.reaction_type == reaction_type:
            db.delete(existing)
        else:
            existing.reaction_type = reaction_type
    else:
        reaction = DiscussionReaction(
            user_id=user_id,
            discussion_id=discussion_id,
            reaction_type=reaction_type,
        )
        db.add(reaction)
    db.commit()
    return get_discussion_reaction_counts(db, discussion_id, user_id=user_id)
