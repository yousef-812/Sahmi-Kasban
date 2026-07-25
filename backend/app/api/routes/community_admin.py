from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.schemas.community import (
    AdminDiscussionActionRequest,
    AdminDiscussionListResponse,
    AdminDiscussionResponse,
    AdminUserActionRequest,
    AdminUserActionResponse,
    DiscussionAuthorResponse,
    DiscussionResponse,
    DiscussionStatus,
)
from app.services.community import DiscussionNotFoundError, DiscussionView
from app.services.community_admin import (
    AdminDiscussionView,
    CommunityAdminActionError,
    CommunityAdminTargetNotFoundError,
    administer_discussion,
    block_community_user,
    list_admin_discussions,
    unblock_community_user,
)

router = APIRouter(prefix="/admin/community", tags=["community-admin"])


def _discussion_response(view: DiscussionView) -> DiscussionResponse:
    discussion = view.discussion
    return DiscussionResponse(
        id=discussion.id,
        ticker=discussion.ticker,
        title=discussion.title,
        content=discussion.content,
        period_type=discussion.period_type,
        status=discussion.status,
        moderation_result=discussion.moderation_result,
        frozen_prediction=discussion.frozen_prediction,
        rejection_code=discussion.rejection_code,
        created_at=discussion.created_at,
        reviewed_at=discussion.reviewed_at,
        published_at=discussion.published_at,
        author=DiscussionAuthorResponse(
            user_id=view.author.id,
            display_name=view.author.display_name,
            avatar_key=view.author.avatar_key,
        ),
    )


def _admin_discussion_response(view: AdminDiscussionView) -> AdminDiscussionResponse:
    return AdminDiscussionResponse(
        discussion=_discussion_response(
            DiscussionView(
                discussion=view.discussion,
                author=view.author,
            )
        ),
        hidden_at=view.discussion.hidden_at,
        open_report_count=view.open_report_count,
        idempotent=view.idempotent,
    )


def _raise_admin_error(exc: Exception) -> None:
    if isinstance(exc, (DiscussionNotFoundError, CommunityAdminTargetNotFoundError)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=str(exc),
    ) from exc


@router.get("/discussions", response_model=AdminDiscussionListResponse)
def admin_discussion_queue(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    discussion_status: DiscussionStatus | None = Query(default="pending_review"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AdminDiscussionListResponse:
    items, total = list_admin_discussions(
        db,
        discussion_status=discussion_status,
        limit=limit,
        offset=offset,
    )
    return AdminDiscussionListResponse(
        items=[_admin_discussion_response(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/discussions/{discussion_id}/action",
    response_model=AdminDiscussionResponse,
)
def admin_discussion_action(
    discussion_id: UUID,
    payload: AdminDiscussionActionRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> AdminDiscussionResponse:
    try:
        view = administer_discussion(
            db,
            admin=admin,
            discussion_id=discussion_id,
            action=payload.action,
            reason_code=payload.reason_code,
            details=payload.details,
            prediction=payload.prediction.model_dump()
            if payload.prediction is not None
            else None,
        )
        db.commit()
    except (
        DiscussionNotFoundError,
        CommunityAdminTargetNotFoundError,
        CommunityAdminActionError,
    ) as exc:
        db.rollback()
        _raise_admin_error(exc)
    return _admin_discussion_response(view)


@router.post(
    "/users/{user_id}/block",
    response_model=AdminUserActionResponse,
)
def admin_block_user(
    user_id: UUID,
    payload: AdminUserActionRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> AdminUserActionResponse:
    try:
        result = block_community_user(
            db,
            admin=admin,
            target_user_id=user_id,
            reason_code=payload.reason_code,
            details=payload.details,
        )
        db.commit()
    except (CommunityAdminTargetNotFoundError, CommunityAdminActionError) as exc:
        db.rollback()
        _raise_admin_error(exc)
    return AdminUserActionResponse(
        user_id=result.user.id,
        status=result.user.status,
        pending_rejected=result.pending_rejected,
        published_hidden=result.published_hidden,
        idempotent=result.idempotent,
    )


@router.post(
    "/users/{user_id}/unblock",
    response_model=AdminUserActionResponse,
)
def admin_unblock_user(
    user_id: UUID,
    payload: AdminUserActionRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> AdminUserActionResponse:
    try:
        result = unblock_community_user(
            db,
            admin=admin,
            target_user_id=user_id,
            reason_code=payload.reason_code,
            details=payload.details,
        )
        db.commit()
    except (CommunityAdminTargetNotFoundError, CommunityAdminActionError) as exc:
        db.rollback()
        _raise_admin_error(exc)
    return AdminUserActionResponse(
        user_id=result.user.id,
        status=result.user.status,
        pending_rejected=result.pending_rejected,
        published_hidden=result.published_hidden,
        idempotent=result.idempotent,
    )
