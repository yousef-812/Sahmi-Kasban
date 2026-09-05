from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.api.dependencies import CurrentAdmin, CurrentUser, DatabaseSession
from app.models.operations import DeveloperFeedback
from app.models.entities import User

router = APIRouter(tags=["feedback"])


class FeedbackCreateRequest(BaseModel):
    message: str = Field(min_length=5, max_length=4000)


class FeedbackCreateResponse(BaseModel):
    id: UUID
    message: str
    status: str
    created_at: datetime


class AdminFeedbackUserItem(BaseModel):
    user_id: UUID
    display_name: str
    email: str


class AdminFeedbackItem(BaseModel):
    id: UUID
    message: str
    status: str
    created_at: datetime
    reviewed_at: datetime | None
    user: AdminFeedbackUserItem


class AdminFeedbackListResponse(BaseModel):
    items: list[AdminFeedbackItem]
    total: int
    limit: int
    offset: int


class AdminFeedbackUpdateRequest(BaseModel):
    status: Literal["new", "reviewed", "resolved", "archived"]


@router.post(
    "/user/feedback",
    response_model=FeedbackCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_developer_feedback(
    payload: FeedbackCreateRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> FeedbackCreateResponse:
    feedback = DeveloperFeedback(
        user_id=current_user.id,
        message=payload.message.strip(),
        status="new",
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return FeedbackCreateResponse(
        id=feedback.id,
        message=feedback.message,
        status=feedback.status,
        created_at=feedback.created_at,
    )


@router.get(
    "/admin/feedbacks",
    response_model=AdminFeedbackListResponse,
)
def list_developer_feedbacks(
    db: DatabaseSession,
    admin: CurrentAdmin,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AdminFeedbackListResponse:
    query = select(DeveloperFeedback, User).join(User, User.id == DeveloperFeedback.user_id)
    if status_filter:
        query = query.where(DeveloperFeedback.status == status_filter)

    total_query = select(func.count(DeveloperFeedback.id))
    if status_filter:
        total_query = total_query.where(DeveloperFeedback.status == status_filter)
    total = db.scalar(total_query) or 0

    rows = db.execute(
        query.order_by(DeveloperFeedback.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    items = [
        AdminFeedbackItem(
            id=fb.id,
            message=fb.message,
            status=fb.status,
            created_at=fb.created_at,
            reviewed_at=fb.reviewed_at,
            user=AdminFeedbackUserItem(
                user_id=usr.id,
                display_name=usr.display_name,
                email=usr.email,
            ),
        )
        for fb, usr in rows
    ]

    return AdminFeedbackListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/admin/feedbacks/{feedback_id}",
    response_model=AdminFeedbackItem,
)
def update_developer_feedback_status(
    feedback_id: UUID,
    payload: AdminFeedbackUpdateRequest,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> AdminFeedbackItem:
    feedback = db.get(DeveloperFeedback, feedback_id)
    if feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )
    feedback.status = payload.status
    feedback.reviewed_at = datetime.now()
    feedback.reviewed_by_user_id = admin.id
    db.commit()
    db.refresh(feedback)

    user = db.get(User, feedback.user_id)
    return AdminFeedbackItem(
        id=feedback.id,
        message=feedback.message,
        status=feedback.status,
        created_at=feedback.created_at,
        reviewed_at=feedback.reviewed_at,
        user=AdminFeedbackUserItem(
            user_id=user.id,
            display_name=user.display_name,
            email=user.email,
        ),
    )
