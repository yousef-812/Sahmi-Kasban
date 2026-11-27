from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUser, DatabaseSession, OptionalUser
from app.core.admin import is_admin_email
from app.schemas.accounts import MessageResponse
from app.schemas.community import (
    DiscussionAuthorResponse,
    DiscussionCommentCreateRequest,
    DiscussionCommentListResponse,
    DiscussionCommentResponse,
)
from app.services.community import CommunityPermissionError, DiscussionNotFoundError
from app.services.discussion_comments import (
    CommentRateLimitError,
    CommentRejectedError,
    CommentView,
    create_comment,
    delete_comment,
    list_comments,
)

router = APIRouter(prefix="/community", tags=["community"])


def _comment_response(view: CommentView, *, viewer_id: UUID | None) -> DiscussionCommentResponse:
    comment = view.comment
    return DiscussionCommentResponse(
        id=comment.id,
        discussion_id=comment.discussion_id,
        parent_id=comment.parent_id,
        content=comment.content,
        created_at=comment.created_at,
        is_mine=viewer_id is not None and comment.user_id == viewer_id,
        author=DiscussionAuthorResponse(
            user_id=view.author.id,
            display_name=view.author.display_name,
            avatar_key=view.author.avatar_key,
            is_admin=is_admin_email(view.author.email),
        ),
    )


@router.get(
    "/discussions/{discussion_id}/comments",
    response_model=DiscussionCommentListResponse,
)
def get_discussion_comments(
    discussion_id: UUID,
    db: DatabaseSession,
    current_user: OptionalUser = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DiscussionCommentListResponse:
    viewer_id = current_user.id if current_user else None
    try:
        views, total = list_comments(db, discussion_id=discussion_id, limit=limit, offset=offset)
    except DiscussionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DiscussionCommentListResponse(
        items=[_comment_response(v, viewer_id=viewer_id) for v in views],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/discussions/{discussion_id}/comments",
    response_model=DiscussionCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_discussion_comment(
    discussion_id: UUID,
    payload: DiscussionCommentCreateRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> DiscussionCommentResponse:
    try:
        view = create_comment(
            db,
            user=current_user,
            discussion_id=discussion_id,
            content=payload.content,
            parent_id=payload.parent_id,
        )
    except DiscussionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CommentRejectedError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except CommentRateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    return _comment_response(view, viewer_id=current_user.id)


@router.delete(
    "/discussions/{discussion_id}/comments/{comment_id}",
    response_model=MessageResponse,
)
def remove_discussion_comment(
    discussion_id: UUID,
    comment_id: UUID,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> MessageResponse:
    try:
        delete_comment(db, user=current_user, discussion_id=discussion_id, comment_id=comment_id)
    except DiscussionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CommunityPermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return MessageResponse(message="Comment deleted")
