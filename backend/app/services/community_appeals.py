from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    CommunityAdminEvent,
    Discussion,
    DiscussionAppeal,
    DiscussionModerationEvent,
    User,
)
from app.services.community import DISCUSSION_COST_POINTS, DiscussionNotFoundError
from app.services.community_admin import CommunityAdminActionError
from app.services.community_ai import normalize_frozen_prediction
from app.services.wallet import debit_points

APPEAL_PUBLISH_ENTRY_TYPE = "discussion_appeal_publish_debit"


class DiscussionAppealError(RuntimeError):
    """Base discussion appeal error."""


class DiscussionAppealConflictError(DiscussionAppealError):
    """Raised when an appeal conflicts with an existing or changed state."""


class DiscussionAppealNotFoundError(DiscussionAppealError):
    """Raised when an appeal cannot be found."""


@dataclass(frozen=True)
class AppealSubmissionResult:
    appeal: DiscussionAppeal
    idempotent: bool


@dataclass(frozen=True)
class AppealView:
    appeal: DiscussionAppeal
    discussion: Discussion
    author: User


@dataclass(frozen=True)
class AppealResolutionResult:
    view: AppealView
    charged_points: int
    idempotent: bool


def _publish_transaction_id(appeal: DiscussionAppeal) -> str:
    return f"discussion:{appeal.discussion_id}:appeal:{appeal.id}:publish"


def submit_discussion_appeal(
    db: Session,
    *,
    user: User,
    discussion_id: UUID,
    message: str,
) -> AppealSubmissionResult:
    discussion = db.scalar(select(Discussion).where(Discussion.id == discussion_id).with_for_update())
    if discussion is None or discussion.user_id != user.id:
        raise DiscussionNotFoundError("Discussion does not exist")
    if discussion.status not in {"rejected", "hidden"}:
        raise DiscussionAppealConflictError("Only rejected or hidden discussions can be appealed")

    cleaned_message = message.strip()
    existing = db.scalar(select(DiscussionAppeal).where(DiscussionAppeal.discussion_id == discussion.id))
    if existing is not None:
        if existing.user_id != user.id or existing.message != cleaned_message:
            raise DiscussionAppealConflictError("This discussion already has a different appeal")
        return AppealSubmissionResult(appeal=existing, idempotent=True)

    appeal = DiscussionAppeal(
        discussion_id=discussion.id,
        user_id=user.id,
        source_status=discussion.status,
        message=cleaned_message,
        status="open",
        resolution_details={},
    )
    db.add(appeal)
    db.flush()
    db.add(
        DiscussionModerationEvent(
            discussion_id=discussion.id,
            actor_type="user",
            actor_user_id=user.id,
            action="appeal_submitted",
            reason_code=discussion.rejection_code,
            details={
                "appeal_id": str(appeal.id),
                "source_status": discussion.status,
            },
        )
    )
    db.flush()
    return AppealSubmissionResult(appeal=appeal, idempotent=False)


def list_user_appeals(
    db: Session,
    *,
    user_id: UUID,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[DiscussionAppeal], int]:
    total = int(
        db.scalar(select(func.count(DiscussionAppeal.id)).where(DiscussionAppeal.user_id == user_id)) or 0
    )
    appeals = db.scalars(
        select(DiscussionAppeal)
        .where(DiscussionAppeal.user_id == user_id)
        .order_by(DiscussionAppeal.created_at.desc(), DiscussionAppeal.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return list(appeals), total


def list_admin_appeals(
    db: Session,
    *,
    appeal_status: str | None = "open",
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[AppealView], int]:
    filters = []
    if appeal_status:
        filters.append(DiscussionAppeal.status == appeal_status)
    total = int(db.scalar(select(func.count(DiscussionAppeal.id)).where(*filters)) or 0)
    rows = db.execute(
        select(DiscussionAppeal, Discussion, User)
        .join(Discussion, Discussion.id == DiscussionAppeal.discussion_id)
        .join(User, User.id == DiscussionAppeal.user_id)
        .where(*filters)
        .order_by(DiscussionAppeal.created_at.asc(), DiscussionAppeal.id.asc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [AppealView(appeal=row[0], discussion=row[1], author=row[2]) for row in rows], total


def _appeal_view(db: Session, appeal: DiscussionAppeal) -> AppealView:
    discussion = db.get(Discussion, appeal.discussion_id)
    author = db.get(User, appeal.user_id)
    if discussion is None or author is None:
        raise DiscussionAppealNotFoundError("Appeal target does not exist")
    return AppealView(appeal=appeal, discussion=discussion, author=author)


def resolve_discussion_appeal(
    db: Session,
    *,
    admin: User,
    appeal_id: UUID,
    decision: str,
    reason_code: str | None = None,
    details: str = "",
    prediction: dict | None = None,
    moment: datetime | None = None,
) -> AppealResolutionResult:
    if decision not in {"accept", "reject"}:
        raise ValueError("Appeal decision must be accept or reject")
    current = moment or datetime.now(UTC)
    appeal = db.scalar(select(DiscussionAppeal).where(DiscussionAppeal.id == appeal_id).with_for_update())
    if appeal is None:
        raise DiscussionAppealNotFoundError("Appeal does not exist")

    final_status = "accepted" if decision == "accept" else "rejected"
    if appeal.status == final_status:
        charged = DISCUSSION_COST_POINTS if appeal.publish_transaction_id else 0
        return AppealResolutionResult(
            view=_appeal_view(db, appeal),
            charged_points=charged,
            idempotent=True,
        )
    if appeal.status != "open":
        raise DiscussionAppealConflictError("Appeal already has a different final decision")

    discussion = db.scalar(select(Discussion).where(Discussion.id == appeal.discussion_id).with_for_update())
    author = db.scalar(select(User).where(User.id == appeal.user_id).with_for_update())
    if discussion is None or author is None:
        raise DiscussionAppealNotFoundError("Appeal target does not exist")
    if discussion.user_id != appeal.user_id:
        raise DiscussionAppealConflictError("Appeal ownership does not match discussion")

    charged_points = 0
    action = "appeal_rejected"
    resolution_details = {"details": details.strip()} if details.strip() else {}
    if decision == "accept":
        if author.status != "active":
            raise CommunityAdminActionError("Suspended users cannot have discussions republished")
        if appeal.source_status == "hidden":
            if discussion.status != "hidden":
                raise DiscussionAppealConflictError(
                    "Hidden discussion state changed before appeal resolution"
                )
            if not discussion.frozen_prediction:
                if prediction is None:
                    raise CommunityAdminActionError(
                        "Restoring this discussion requires a structured prediction"
                    )
                discussion.frozen_prediction = normalize_frozen_prediction(
                    discussion,
                    prediction,
                    moment=current,
                )
            discussion.status = "published"
            discussion.hidden_at = None
            action = "appeal_restored"
        elif appeal.source_status == "rejected":
            if discussion.status != "rejected":
                raise DiscussionAppealConflictError(
                    "Rejected discussion state changed before appeal resolution"
                )
            if prediction is None:
                raise CommunityAdminActionError(
                    "Accepting a rejected discussion appeal requires a prediction"
                )
            frozen_prediction = normalize_frozen_prediction(
                discussion,
                prediction,
                moment=current,
            )
            transaction_id = _publish_transaction_id(appeal)
            debit_points(
                db,
                user_id=author.id,
                amount_points=DISCUSSION_COST_POINTS,
                transaction_id=transaction_id,
                entry_type=APPEAL_PUBLISH_ENTRY_TYPE,
                reference_type="discussion_appeal",
                reference_id=str(appeal.id),
                details={"discussion_id": str(discussion.id)},
            )
            appeal.publish_transaction_id = transaction_id
            charged_points = DISCUSSION_COST_POINTS
            discussion.status = "published"
            discussion.published_at = current
            discussion.hidden_at = None
            discussion.reviewed_at = current
            discussion.rejection_code = None
            discussion.frozen_prediction = frozen_prediction
            action = "appeal_published"
        else:
            raise DiscussionAppealConflictError("Appeal source status is unsupported")

        moderation_result = dict(discussion.moderation_result)
        moderation_result["appeal_resolution"] = {
            "appeal_id": str(appeal.id),
            "decision": "accept",
            "resolved_at": current.isoformat(),
            "charged_points": charged_points,
        }
        discussion.moderation_result = moderation_result
    else:
        if not reason_code:
            raise CommunityAdminActionError("Rejecting an appeal requires a reason code")

    appeal.status = final_status
    appeal.resolved_at = current
    appeal.resolved_by_user_id = admin.id
    appeal.resolution_reason_code = reason_code
    appeal.resolution_details = {
        **resolution_details,
        "charged_points": charged_points,
    }
    db.add(
        DiscussionModerationEvent(
            discussion_id=discussion.id,
            actor_type="admin",
            actor_user_id=admin.id,
            action=action,
            reason_code=reason_code,
            details={
                "appeal_id": str(appeal.id),
                "charged_points": charged_points,
                **resolution_details,
            },
        )
    )
    db.add(
        CommunityAdminEvent(
            actor_user_id=admin.id,
            target_user_id=author.id,
            discussion_id=discussion.id,
            action=f"appeal_{decision}",
            reason_code=reason_code,
            details={
                "appeal_id": str(appeal.id),
                "charged_points": charged_points,
                **resolution_details,
            },
        )
    )
    db.flush()
    return AppealResolutionResult(
        view=AppealView(appeal=appeal, discussion=discussion, author=author),
        charged_points=charged_points,
        idempotent=False,
    )
