from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.models import DiscussionAppeal
from app.schemas.community import (
    AdminAppealListResponse,
    AdminAppealResolveRequest,
    AdminAppealResponse,
    AppealStatus,
    DiscussionAppealResponse,
    DiscussionAuthorResponse,
    DiscussionResponse,
)
from app.services.community import DiscussionView
from app.services.community_admin import CommunityAdminActionError
from app.services.community_appeals import (
    AppealView,
    DiscussionAppealConflictError,
    DiscussionAppealNotFoundError,
    list_admin_appeals,
    resolve_discussion_appeal,
)
from app.services.wallet import InsufficientBalanceError, points_to_coins

router = APIRouter(prefix="/admin/community", tags=["community-admin-appeals"])
AdminAppealStatusQuery = Annotated[AppealStatus | None, Query()]


def _appeal_response(appeal: DiscussionAppeal) -> DiscussionAppealResponse:
    return DiscussionAppealResponse(
        id=appeal.id,
        discussion_id=appeal.discussion_id,
        user_id=appeal.user_id,
        source_status=appeal.source_status,
        message=appeal.message,
        status=appeal.status,
        created_at=appeal.created_at,
        resolved_at=appeal.resolved_at,
        resolution_reason_code=appeal.resolution_reason_code,
        resolution_details=appeal.resolution_details,
    )


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


def _admin_appeal_response(
    view: AppealView,
    *,
    charged_points: int = 0,
    idempotent: bool = False,
) -> AdminAppealResponse:
    return AdminAppealResponse(
        appeal=_appeal_response(view.appeal),
        discussion=_discussion_response(DiscussionView(discussion=view.discussion, author=view.author)),
        charged_points=charged_points,
        charged_coins=points_to_coins(charged_points),
        idempotent=idempotent,
    )


@router.get("/appeals", response_model=AdminAppealListResponse)
def admin_appeal_queue(
    db: DatabaseSession,
    _admin: CurrentAdmin,
    appeal_status: AdminAppealStatusQuery = "open",
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AdminAppealListResponse:
    appeals, total = list_admin_appeals(
        db,
        appeal_status=appeal_status,
        limit=limit,
        offset=offset,
    )
    return AdminAppealListResponse(
        items=[_admin_appeal_response(view) for view in appeals],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/appeals/{appeal_id}/resolve",
    response_model=AdminAppealResponse,
)
def admin_resolve_appeal(
    appeal_id: UUID,
    payload: AdminAppealResolveRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> AdminAppealResponse:
    try:
        result = resolve_discussion_appeal(
            db,
            admin=admin,
            appeal_id=appeal_id,
            decision=payload.decision,
            reason_code=payload.reason_code,
            details=payload.details,
            prediction=payload.prediction.model_dump() if payload.prediction is not None else None,
        )
        db.commit()
    except DiscussionAppealNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except InsufficientBalanceError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Appeal accepted, but the user does not have 0.5 coin available",
        ) from exc
    except (DiscussionAppealConflictError, CommunityAdminActionError) as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return _admin_appeal_response(
        result.view,
        charged_points=result.charged_points,
        idempotent=result.idempotent,
    )
