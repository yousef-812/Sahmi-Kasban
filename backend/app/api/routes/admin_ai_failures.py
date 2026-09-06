from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.api.dependencies import CurrentAdmin, DatabaseSession
from app.models import AiFailureLog, User

router = APIRouter(prefix="/admin/ai-failures", tags=["admin_ai_failures"])


class AiFailureLogItem(BaseModel):
    id: str
    user_id: str | None
    user_name: str
    user_email: str
    ticker: str | None
    question: str
    error_message: str
    error_traceback: str | None
    created_at: str


class ClearCooldownResponse(BaseModel):
    success: bool
    message: str
    user_id: str


@router.get("", response_model=list[AiFailureLogItem])
def list_ai_failures(
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> list[AiFailureLogItem]:
    logs = db.scalars(
        select(AiFailureLog).order_by(AiFailureLog.created_at.desc()).limit(100)
    ).all()

    return [
        AiFailureLogItem(
            id=str(log.id),
            user_id=str(log.user_id) if log.user_id else None,
            user_name=log.user_name,
            user_email=log.user_email,
            ticker=log.ticker,
            question=log.question,
            error_message=log.error_message,
            error_traceback=log.error_traceback,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.post("/users/{user_id}/clear-cooldown", response_model=ClearCooldownResponse)
def clear_user_ai_cooldown(
    user_id: UUID,
    db: DatabaseSession,
    admin: CurrentAdmin,
) -> ClearCooldownResponse:
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود.",
        )

    user.ai_cooldown_until = None
    db.commit()

    return ClearCooldownResponse(
        success=True,
        message="تم إلغاء الحظر الإجباري عن المساعد الذكي لهذا المستخدم بنجاح.",
        user_id=str(user_id),
    )
