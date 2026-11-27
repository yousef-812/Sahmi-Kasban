from __future__ import annotations

from fastapi import APIRouter, status

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.api.routes.community import _discussion_response
from app.schemas.community import AdminGeneralPostRequest, DiscussionResponse
from app.services.general_posts import create_general_post

router = APIRouter(prefix="/admin/community", tags=["community-admin"])


@router.post(
    "/posts",
    response_model=DiscussionResponse,
    status_code=status.HTTP_201_CREATED,
)
def publish_general_post(
    payload: AdminGeneralPostRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> DiscussionResponse:
    """Publish an official general (non-prediction) post from the admin account."""
    view, _already = create_general_post(
        db,
        admin=admin,
        submission_key=payload.submission_key,
        title=payload.title,
        content=payload.content,
        ticker=payload.ticker,
    )
    return _discussion_response(view, db=db, current_user_id=admin.id, include_moderation=False)
