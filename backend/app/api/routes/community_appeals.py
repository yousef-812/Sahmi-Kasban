from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.community import (
    DiscussionAppealCreateRequest,
    DiscussionAppealListResponse,
    DiscussionAppealResponse,
    DiscussionAppealSubmissionResponse,
)
from app.services.community import DiscussionNotFoundError
from app.services.community_appeals import (
    DiscussionAppealConflictError,
    list_user_appeals,
    submit_discussion_appeal,
)

router = APIRouter(prefix="/community", tags=["community-appeals"])


def appeal_response(appeal) -> DiscussionAppealResponse:
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


@router.post(
    "/discussions/{discussion_id}/appeals",
    response_model=DiscussionAppealSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_discussion_appeal(
    discussion_id: UUID,
    payload: DiscussionAppealCreateRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> DiscussionAppealSubmissionResponse:
    try:
        result = submit_discussion_appeal(
            db,
            user=current_user,
            discussion_id=discussion_id,
            message=payload.message,
        )
        db.commit()
    except DiscussionNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DiscussionAppealConflictError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return DiscussionAppealSubmissionResponse(
        appeal=appeal_response(result.appeal),
        idempotent=result.idempotent,
    )


@router.get("/appeals/mine", response_model=DiscussionAppealListResponse)
def my_discussion_appeals(
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DiscussionAppealListResponse:
    appeals, total = list_user_appeals(
        db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return DiscussionAppealListResponse(
        items=[appeal_response(appeal) for appeal in appeals],
        total=total,
        limit=limit,
        offset=offset,
    )
