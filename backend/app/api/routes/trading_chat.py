from __future__ import annotations

from datetime import UTC, date, datetime, time
from typing import Annotated
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.config import get_settings
from app.models import DailyChatMessage, DailyChatSessionVote, Notification, PushDevice, User
from app.services.notifications import FCMPushSender, _decrypt_token, create_notification
from app.services.operations_settings import get_bool_setting

router = APIRouter(prefix="/trading-chat", tags=["trading_chat"])

CHAT_START_HOUR = 10
CHAT_START_MINUTE = 0
CHAT_END_HOUR = 14
CHAT_END_MINUTE = 30


def get_cairo_now() -> datetime:
    settings = get_settings()
    tz = ZoneInfo(settings.market_timezone)
    return datetime.now(UTC).astimezone(tz)


def get_cairo_today() -> date:
    return get_cairo_now().date()


def is_chat_active_now(now: datetime | None = None) -> bool:
    cairo = now or get_cairo_now()
    start = datetime.combine(cairo.date(), time(CHAT_START_HOUR, CHAT_START_MINUTE), tzinfo=cairo.tzinfo)
    end = datetime.combine(cairo.date(), time(CHAT_END_HOUR, CHAT_END_MINUTE), tzinfo=cairo.tzinfo)
    return start <= cairo <= end


class ChatStatusResponse(BaseModel):
    session_date: str
    is_session_open: bool
    chat_start_hour: int = CHAT_START_HOUR
    chat_end_hour: int = CHAT_END_HOUR
    chat_end_minute: int = CHAT_END_MINUTE


class ChatMessageItem(BaseModel):
    id: str
    user_name: str
    content: str
    created_at: str


class PostChatMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


def _send_chat_open_notifications(db, session_date: str) -> int:
    if not get_bool_setting(db, "notifications_enabled"):
        return 0
    users = db.scalars(
        select(User).where(User.status == "active", User.email_verified.is_(True))
    ).all()
    push_sender = FCMPushSender()
    title = "غرفة التداول المباشرة مفتوحة الآن"
    body = "غرفة الشات اليومية مفتوحة من 10:00 صباحاً حتى 2:30 مساءً. انضم الآن!"
    data = {"route": "/trading-chat", "session_date": session_date}
    sent = 0
    for user in users:
        create_notification(
            db,
            user_id=user.id,
            title=title,
            body=body,
            category="trading_chat",
            data=data,
        )
        devices = db.scalars(
            select(PushDevice).where(
                PushDevice.user_id == user.id,
                PushDevice.enabled.is_(True),
            )
        ).all()
        for device in devices:
            try:
                push_sender.send(
                    token=_decrypt_token(device.encrypted_token),
                    title=title,
                    body=body,
                    data=data,
                )
                sent += 1
            except Exception:
                pass
    db.flush()
    return sent


def send_event_notification(
    db,
    *,
    title: str,
    body: str,
    category: str,
    data: dict | None = None,
) -> int:
    if not get_bool_setting(db, "notifications_enabled"):
        return 0
    users = db.scalars(
        select(User).where(User.status == "active", User.email_verified.is_(True))
    ).all()
    push_sender = FCMPushSender()
    payload_data = data or {}
    sent = 0
    for user in users:
        create_notification(
            db,
            user_id=user.id,
            title=title,
            body=body,
            category=category,
            data=payload_data,
        )
        devices = db.scalars(
            select(PushDevice).where(
                PushDevice.user_id == user.id,
                PushDevice.enabled.is_(True),
            )
        ).all()
        for device in devices:
            try:
                push_sender.send(
                    token=_decrypt_token(device.encrypted_token),
                    title=title,
                    body=body,
                    data=payload_data,
                )
                sent += 1
            except Exception:
                pass
    db.flush()
    return sent


@router.get("/status", response_model=ChatStatusResponse)
def get_trading_chat_status(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ChatStatusResponse:
    cairo_now = get_cairo_now()
    return ChatStatusResponse(
        session_date=cairo_now.date().isoformat(),
        is_session_open=is_chat_active_now(cairo_now),
    )


@router.get("/messages", response_model=list[ChatMessageItem])
def get_chat_messages(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> list[ChatMessageItem]:
    cairo_today = get_cairo_today()
    messages = db.scalars(
        select(DailyChatMessage)
        .where(DailyChatMessage.session_date == cairo_today)
        .order_by(DailyChatMessage.created_at.asc())
    ).all()
    return [
        ChatMessageItem(
            id=str(msg.id),
            user_name=msg.user_name,
            content=msg.content,
            created_at=msg.created_at.isoformat(),
        )
        for msg in messages
    ]


@router.post("/messages", response_model=ChatMessageItem)
def post_chat_message(
    body: PostChatMessageRequest,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ChatMessageItem:
    cairo_now = get_cairo_now()
    cairo_today = cairo_now.date()

    if not is_chat_active_now(cairo_now):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غرفة التداول المباشر متاحة فقط بين الساعة 10:00 صباحاً و 2:30 مساءً بتوقيت مصر.",
        )

    author_name = current_user.display_name or current_user.full_name or "متداول"

    msg = DailyChatMessage(
        user_id=current_user.id,
        session_date=cairo_today,
        user_name=author_name,
        content=body.content.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return ChatMessageItem(
        id=str(msg.id),
        user_name=msg.user_name,
        content=msg.content,
        created_at=msg.created_at.isoformat(),
    )
