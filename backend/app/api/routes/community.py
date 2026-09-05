from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sahmi_kasban.ai import SahmiAIService

from app.api.dependencies import CurrentUser, DatabaseSession, OptionalUser
from app.schemas.community import (
    DiscussionAuthorResponse,
    DiscussionCreateRequest,
    DiscussionListResponse,
    DiscussionReactionRequest,
    DiscussionReactionResponse,
    DiscussionReportRequest,
    DiscussionReportResponse,
    DiscussionResponse,
    DiscussionSubmissionResponse,
    UserMuteResponse,
)
from app.services.community import (
    DISCUSSION_COST_POINTS,
    CommunityConflictError,
    DiscussionNotFoundError,
    DiscussionReportError,
    DiscussionView,
    UserMuteError,
    get_discussion_reaction_counts,
    get_discussion_view,
    increment_discussion_view,
    list_published_discussions,
    list_user_discussions,
    mute_user,
    report_discussion,
    toggle_discussion_reaction,
    unmute_user,
)
from app.services.community_ai import (
    get_community_ai_service,
    review_pending_discussion,
)
from app.services.community_safety import (
    CommunityRateLimitError,
    create_safe_discussion,
)
from app.services.wallet import (
    InsufficientBalanceError,
    get_wallet_account,
    points_to_coins,
)

router = APIRouter(prefix="/community", tags=["community"])
CommunityAIService = Annotated[SahmiAIService, Depends(get_community_ai_service)]


def _discussion_response(
    view: DiscussionView,
    *,
    db: DatabaseSession,
    current_user_id: UUID | None = None,
    include_moderation: bool,
) -> DiscussionResponse:
    discussion = view.discussion
    agree_count, disagree_count, user_reaction = get_discussion_reaction_counts(
        db,
        discussion.id,
        user_id=current_user_id,
    )
    return DiscussionResponse(
        id=discussion.id,
        ticker=discussion.ticker,
        title=discussion.title,
        content=discussion.content,
        period_type=discussion.period_type,
        status=discussion.status,
        moderation_result=discussion.moderation_result if include_moderation else {},
        frozen_prediction=discussion.frozen_prediction,
        rejection_code=discussion.rejection_code if include_moderation else None,
        created_at=discussion.created_at,
        reviewed_at=discussion.reviewed_at,
        published_at=discussion.published_at,
        views_count=discussion.views_count or 0,
        agree_count=agree_count,
        disagree_count=disagree_count,
        user_reaction=user_reaction,
        author=DiscussionAuthorResponse(
            user_id=view.author.id,
            display_name=view.author.display_name,
            avatar_key=view.author.avatar_key,
        ),
    )


@router.post(
    "/discussions",
    response_model=DiscussionSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_discussion(
    payload: DiscussionCreateRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
    ai_service: CommunityAIService,
) -> DiscussionSubmissionResponse:
    try:
        result = create_safe_discussion(
            db,
            user=current_user,
            submission_key=payload.submission_key,
            ticker=payload.ticker,
            title=payload.title,
            content=payload.content,
            period_type=payload.period_type,
        )
        db.commit()

        discussion = result.discussion
        if discussion.status == "pending_review":
            ai_review = await review_pending_discussion(
                db,
                discussion_id=discussion.id,
                ai_service=ai_service,
            )
            discussion = ai_review.discussion
            db.commit()
    except InsufficientBalanceError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except CommunityRateLimitError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc
    except CommunityConflictError as exc:
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

    account = get_wallet_account(db, current_user.id)
    view = DiscussionView(discussion=discussion, author=result.author)
    held_points = DISCUSSION_COST_POINTS if discussion.status == "pending_review" else 0
    return DiscussionSubmissionResponse(
        discussion=_discussion_response(view, db=db, current_user_id=current_user.id, include_moderation=True),
        held_points=held_points,
        held_coins=points_to_coins(held_points),
        balance_points=account.balance_points,
        balance_coins=points_to_coins(account.balance_points),
        idempotent=result.idempotent,
    )


@router.get("/discussions", response_model=DiscussionListResponse)
def community_discussions(
    db: DatabaseSession,
    current_user: OptionalUser = None,
    ticker: str | None = Query(default=None, min_length=2, max_length=24),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DiscussionListResponse:
    viewer_user_id = current_user.id if current_user else None
    items, total = list_published_discussions(
        db,
        viewer_user_id=viewer_user_id,
        ticker=ticker,
        limit=limit,
        offset=offset,
    )
    return DiscussionListResponse(
        items=[_discussion_response(item, db=db, current_user_id=viewer_user_id, include_moderation=False) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/discussions/mine", response_model=DiscussionListResponse)
def my_discussions(
    db: DatabaseSession,
    current_user: CurrentUser,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DiscussionListResponse:
    items, total = list_user_discussions(
        db,
        user=current_user,
        limit=limit,
        offset=offset,
    )
    return DiscussionListResponse(
        items=[_discussion_response(item, db=db, current_user_id=current_user.id, include_moderation=True) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/discussions/{discussion_id}",
    response_model=DiscussionResponse,
)
def community_discussion(
    discussion_id: UUID,
    db: DatabaseSession,
    current_user: OptionalUser = None,
) -> DiscussionResponse:
    try:
        view = get_discussion_view(db, discussion_id)
        increment_discussion_view(db, discussion_id)
    except DiscussionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    viewer_user_id = current_user.id if current_user else None
    if view.discussion.status != "published" and (viewer_user_id is None or view.discussion.user_id != viewer_user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion does not exist",
        )
    return _discussion_response(
        view,
        db=db,
        current_user_id=viewer_user_id,
        include_moderation=view.discussion.user_id == viewer_user_id if viewer_user_id else False,
    )


@router.post(
    "/discussions/{discussion_id}/reactions",
    response_model=DiscussionReactionResponse,
)
def react_to_discussion(
    discussion_id: UUID,
    payload: DiscussionReactionRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> DiscussionReactionResponse:
    try:
        agree_count, disagree_count, user_reaction = toggle_discussion_reaction(
            db,
            user_id=current_user.id,
            discussion_id=discussion_id,
            reaction_type=payload.reaction_type,
        )
    except DiscussionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return DiscussionReactionResponse(
        discussion_id=discussion_id,
        agree_count=agree_count,
        disagree_count=disagree_count,
        user_reaction=user_reaction,
    )


@router.post(
    "/discussions/{discussion_id}/reports",
    response_model=DiscussionReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_discussion_report(
    discussion_id: UUID,
    payload: DiscussionReportRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> DiscussionReportResponse:
    try:
        result = report_discussion(
            db,
            reporter=current_user,
            discussion_id=discussion_id,
            reason_code=payload.reason_code,
            details=payload.details,
        )
        db.commit()
    except DiscussionNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DiscussionReportError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return DiscussionReportResponse(
        report_id=result.report.id,
        discussion_id=result.report.discussion_id,
        status=result.report.status,
        idempotent=result.idempotent,
    )


@router.put(
    "/users/{user_id}/mute",
    response_model=UserMuteResponse,
)
def mute_community_user(
    user_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> UserMuteResponse:
    try:
        result = mute_user(
            db,
            muter_user_id=current_user.id,
            muted_user_id=user_id,
        )
        db.commit()
    except UserMuteError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return UserMuteResponse(
        muted_user_id=result.muted_user_id,
        muted=result.muted,
        idempotent=result.idempotent,
    )


@router.delete(
    "/users/{user_id}/mute",
    response_model=UserMuteResponse,
)
def unmute_community_user(
    user_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> UserMuteResponse:
    result = unmute_user(
        db,
        muter_user_id=current_user.id,
        muted_user_id=user_id,
    )
    db.commit()
    return UserMuteResponse(
        muted_user_id=result.muted_user_id,
        muted=result.muted,
        idempotent=result.idempotent,
    )
