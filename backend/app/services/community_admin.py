from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    CommunityAdminEvent,
    Discussion,
    DiscussionModerationEvent,
    DiscussionReport,
    User,
)
from app.services.community import (
    CommunityConflictError,
    DiscussionNotFoundError,
    apply_moderation_decision,
)
from app.services.community_ai import normalize_frozen_prediction


class CommunityAdminError(RuntimeError):
    """Base community administration error."""


class CommunityAdminTargetNotFoundError(CommunityAdminError):
    """Raised when an administration target does not exist."""


class CommunityAdminActionError(CommunityAdminError):
    """Raised when an administration action is invalid for the target state."""


@dataclass(frozen=True)
class AdminDiscussionView:
    discussion: Discussion
    author: User
    open_report_count: int
    idempotent: bool = False


@dataclass(frozen=True)
class AdminUserActionResult:
    user: User
    pending_rejected: int
    published_hidden: int
    idempotent: bool


def _admin_event(
    db: Session,
    *,
    actor_user_id: UUID,
    action: str,
    reason_code: str | None = None,
    target_user_id: UUID | None = None,
    discussion_id: UUID | None = None,
    details: dict | None = None,
) -> CommunityAdminEvent:
    event = CommunityAdminEvent(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        discussion_id=discussion_id,
        action=action,
        reason_code=reason_code,
        details=details or {},
    )
    db.add(event)
    db.flush()
    return event


def _discussion_event(
    db: Session,
    *,
    discussion: Discussion,
    actor_user_id: UUID,
    action: str,
    reason_code: str | None = None,
    details: dict | None = None,
) -> None:
    db.add(
        DiscussionModerationEvent(
            discussion_id=discussion.id,
            actor_type="admin",
            actor_user_id=actor_user_id,
            action=action,
            reason_code=reason_code,
            details=details or {},
        )
    )


def _resolve_open_reports(
    db: Session,
    *,
    discussion_id: UUID,
    admin_user_id: UUID,
    resolution_action: str,
    reason_code: str | None,
    moment: datetime,
) -> int:
    reports = db.scalars(
        select(DiscussionReport)
        .where(
            DiscussionReport.discussion_id == discussion_id,
            DiscussionReport.status == "open",
        )
        .with_for_update()
    ).all()
    for report in reports:
        report.status = "resolved"
        report.resolved_at = moment
        report.resolved_by_user_id = admin_user_id
        report.resolution_details = {
            "action": resolution_action,
            "reason_code": reason_code,
        }
    return len(reports)


def _open_report_count(db: Session, discussion_id: UUID) -> int:
    return int(
        db.scalar(
            select(func.count(DiscussionReport.id)).where(
                DiscussionReport.discussion_id == discussion_id,
                DiscussionReport.status == "open",
            )
        )
        or 0
    )


def _admin_view(
    db: Session,
    discussion: Discussion,
    *,
    idempotent: bool = False,
) -> AdminDiscussionView:
    author = db.get(User, discussion.user_id)
    if author is None:
        raise CommunityAdminTargetNotFoundError("Discussion author does not exist")
    return AdminDiscussionView(
        discussion=discussion,
        author=author,
        open_report_count=_open_report_count(db, discussion.id),
        idempotent=idempotent,
    )


def list_admin_discussions(
    db: Session,
    *,
    discussion_status: str | None = "pending_review",
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[AdminDiscussionView], int]:
    report_count = (
        select(func.count(DiscussionReport.id))
        .where(
            DiscussionReport.discussion_id == Discussion.id,
            DiscussionReport.status == "open",
        )
        .correlate(Discussion)
        .scalar_subquery()
    )
    filters = []
    if discussion_status:
        filters.append(Discussion.status == discussion_status)

    total = int(db.scalar(select(func.count(Discussion.id)).where(*filters)) or 0)
    rows = db.execute(
        select(Discussion, User, report_count.label("open_report_count"))
        .join(User, User.id == Discussion.user_id)
        .where(*filters)
        .order_by(Discussion.created_at.asc(), Discussion.id.asc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [
        AdminDiscussionView(
            discussion=row[0],
            author=row[1],
            open_report_count=int(row[2] or 0),
        )
        for row in rows
    ], total


def administer_discussion(
    db: Session,
    *,
    admin: User,
    discussion_id: UUID,
    action: str,
    reason_code: str | None = None,
    details: str = "",
    prediction: dict | None = None,
    moment: datetime | None = None,
) -> AdminDiscussionView:
    current = moment or datetime.now(UTC)
    discussion = db.scalar(
        select(Discussion)
        .where(Discussion.id == discussion_id)
        .with_for_update()
    )
    if discussion is None:
        raise DiscussionNotFoundError("Discussion does not exist")

    detail_payload = {"details": details.strip()} if details.strip() else {}
    idempotent = False

    if action == "approve":
        if discussion.status == "published":
            idempotent = True
        elif discussion.status != "pending_review":
            raise CommunityAdminActionError(
                "Only pending discussions can be manually approved"
            )
        else:
            if prediction is None:
                raise CommunityAdminActionError(
                    "Manual approval requires a structured prediction"
                )
            try:
                frozen_prediction = normalize_frozen_prediction(
                    discussion,
                    prediction,
                    moment=current,
                )
                discussion = apply_moderation_decision(
                    db,
                    discussion_id=discussion.id,
                    decision="accept",
                    actor_type="admin",
                    actor_user_id=admin.id,
                    moderation_details={
                        "manual": True,
                        **detail_payload,
                    },
                    frozen_prediction=frozen_prediction,
                    moment=current,
                )
            except (CommunityConflictError, ValueError) as exc:
                raise CommunityAdminActionError(str(exc)) from exc
    elif action == "reject":
        if discussion.status == "rejected":
            idempotent = True
        elif discussion.status != "pending_review":
            raise CommunityAdminActionError(
                "Only pending discussions can be manually rejected"
            )
        else:
            if not reason_code:
                raise CommunityAdminActionError("Manual rejection requires a reason code")
            try:
                discussion = apply_moderation_decision(
                    db,
                    discussion_id=discussion.id,
                    decision="reject",
                    actor_type="admin",
                    actor_user_id=admin.id,
                    reason_code=reason_code,
                    moderation_details={
                        "manual": True,
                        **detail_payload,
                    },
                    moment=current,
                )
            except CommunityConflictError as exc:
                raise CommunityAdminActionError(str(exc)) from exc
    elif action == "hide":
        if discussion.status == "hidden":
            idempotent = True
        elif discussion.status != "published":
            raise CommunityAdminActionError("Only published discussions can be hidden")
        else:
            if not reason_code:
                raise CommunityAdminActionError("Hiding requires a reason code")
            discussion.status = "hidden"
            discussion.hidden_at = current
            resolved_reports = _resolve_open_reports(
                db,
                discussion_id=discussion.id,
                admin_user_id=admin.id,
                resolution_action="hidden",
                reason_code=reason_code,
                moment=current,
            )
            detail_payload["resolved_reports"] = resolved_reports
            _discussion_event(
                db,
                discussion=discussion,
                actor_user_id=admin.id,
                action="hidden",
                reason_code=reason_code,
                details=detail_payload,
            )
    elif action == "restore":
        if discussion.status == "published":
            idempotent = True
        elif discussion.status != "hidden":
            raise CommunityAdminActionError("Only hidden discussions can be restored")
        else:
            discussion.status = "published"
            discussion.hidden_at = None
            _discussion_event(
                db,
                discussion=discussion,
                actor_user_id=admin.id,
                action="restored",
                reason_code=reason_code,
                details=detail_payload,
            )
    else:
        raise CommunityAdminActionError("Unsupported community administration action")

    if not idempotent:
        _admin_event(
            db,
            actor_user_id=admin.id,
            target_user_id=discussion.user_id,
            discussion_id=discussion.id,
            action=f"discussion_{action}",
            reason_code=reason_code,
            details=detail_payload,
        )
    db.flush()
    return _admin_view(db, discussion, idempotent=idempotent)


def block_community_user(
    db: Session,
    *,
    admin: User,
    target_user_id: UUID,
    reason_code: str,
    details: str = "",
    moment: datetime | None = None,
) -> AdminUserActionResult:
    if admin.id == target_user_id:
        raise CommunityAdminActionError("Administrators cannot block themselves")

    current = moment or datetime.now(UTC)
    target = db.scalar(
        select(User).where(User.id == target_user_id).with_for_update()
    )
    if target is None:
        raise CommunityAdminTargetNotFoundError("User does not exist")
    if target.status == "suspended":
        return AdminUserActionResult(
            user=target,
            pending_rejected=0,
            published_hidden=0,
            idempotent=True,
        )
    if target.status != "active":
        raise CommunityAdminActionError("Only active users can be blocked")

    discussions = db.scalars(
        select(Discussion)
        .where(Discussion.user_id == target.id)
        .order_by(Discussion.created_at, Discussion.id)
        .with_for_update()
    ).all()
    pending_rejected = 0
    published_hidden = 0
    for discussion in discussions:
        if discussion.status == "pending_review":
            try:
                apply_moderation_decision(
                    db,
                    discussion_id=discussion.id,
                    decision="reject",
                    actor_type="admin",
                    actor_user_id=admin.id,
                    reason_code="account_suspended",
                    moderation_details={
                        "manual": True,
                        "block_reason_code": reason_code,
                    },
                    moment=current,
                )
            except CommunityConflictError as exc:
                raise CommunityAdminActionError(str(exc)) from exc
            pending_rejected += 1
        elif discussion.status == "published":
            discussion.status = "hidden"
            discussion.hidden_at = current
            resolved_reports = _resolve_open_reports(
                db,
                discussion_id=discussion.id,
                admin_user_id=admin.id,
                resolution_action="account_suspended",
                reason_code=reason_code,
                moment=current,
            )
            _discussion_event(
                db,
                discussion=discussion,
                actor_user_id=admin.id,
                action="hidden",
                reason_code="account_suspended",
                details={
                    "block_reason_code": reason_code,
                    "resolved_reports": resolved_reports,
                },
            )
            published_hidden += 1

    target.status = "suspended"
    target.auth_version += 1
    _admin_event(
        db,
        actor_user_id=admin.id,
        target_user_id=target.id,
        action="user_blocked",
        reason_code=reason_code,
        details={
            "details": details.strip(),
            "pending_rejected": pending_rejected,
            "published_hidden": published_hidden,
        },
    )
    db.flush()
    return AdminUserActionResult(
        user=target,
        pending_rejected=pending_rejected,
        published_hidden=published_hidden,
        idempotent=False,
    )


def unblock_community_user(
    db: Session,
    *,
    admin: User,
    target_user_id: UUID,
    reason_code: str,
    details: str = "",
) -> AdminUserActionResult:
    if admin.id == target_user_id:
        raise CommunityAdminActionError("Administrators cannot change their own status")

    target = db.scalar(
        select(User).where(User.id == target_user_id).with_for_update()
    )
    if target is None:
        raise CommunityAdminTargetNotFoundError("User does not exist")
    if target.status == "active":
        return AdminUserActionResult(
            user=target,
            pending_rejected=0,
            published_hidden=0,
            idempotent=True,
        )
    if target.status != "suspended":
        raise CommunityAdminActionError("Only suspended users can be reactivated")

    target.status = "active"
    target.auth_version += 1
    _admin_event(
        db,
        actor_user_id=admin.id,
        target_user_id=target.id,
        action="user_unblocked",
        reason_code=reason_code,
        details={"details": details.strip()},
    )
    db.flush()
    return AdminUserActionResult(
        user=target,
        pending_rejected=0,
        published_hidden=0,
        idempotent=False,
    )
