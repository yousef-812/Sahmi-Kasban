from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Annotated
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.api.dependencies import CurrentUser, DatabaseSession
from app.core.config import get_settings
from app.models import DailyChatMessage, DailyChatSessionVote
from app.services.wallet import InsufficientBalanceError, debit_points

router = APIRouter(prefix="/trading-chat", tags=["trading_chat"])

VOTE_COST_POINTS = 50  # 0.5 coins
VOTE_TARGET = 40


def get_cairo_now() -> datetime:
    settings = get_settings()
    tz = ZoneInfo(settings.market_timezone)
    return datetime.now(UTC).astimezone(tz)


def get_cairo_today() -> date:
    return get_cairo_now().date()


def is_cairo_trading_hours(now: datetime) -> bool:
    # 09:00 to 15:00 Cairo time
    hour = now.hour
    return 9 <= hour < 15


class ChatStatusResponse(BaseModel):
    session_date: str
    votes_count: int
    votes_target: int = VOTE_TARGET
    is_unlocked: bool
    is_session_open: bool
    has_voted: bool
    coins_cost: float = 0.5


class VoteRequestResponse(BaseModel):
    success: bool
    message: str
    votes_count: int
    is_unlocked: bool


class PostChatMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class ChatMessageItem(BaseModel):
    id: str
    user_name: str
    content: str
    created_at: str


@router.get("/status", response_model=ChatStatusResponse)
def get_trading_chat_status(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> ChatStatusResponse:
    cairo_now = get_cairo_now()
    cairo_today = cairo_now.date()

    votes_count = db.scalar(
        select(func.count(DailyChatSessionVote.id)).where(
            DailyChatSessionVote.session_date == cairo_today,
            DailyChatSessionVote.refunded.is_(False),
        )
    ) or 0

    user_vote = db.scalar(
        select(DailyChatSessionVote).where(
            DailyChatSessionVote.session_date == cairo_today,
            DailyChatSessionVote.user_id == current_user.id,
            DailyChatSessionVote.refunded.is_(False),
        )
    )

    is_unlocked = votes_count >= VOTE_TARGET
    is_session_open = is_unlocked and is_cairo_trading_hours(cairo_now)

    return ChatStatusResponse(
        session_date=cairo_today.isoformat(),
        votes_count=votes_count,
        votes_target=VOTE_TARGET,
        is_unlocked=is_unlocked,
        is_session_open=is_session_open,
        has_voted=user_vote is not None,
        coins_cost=0.5,
    )


@router.post("/vote", response_model=VoteRequestResponse)
def vote_to_open_chat(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> VoteRequestResponse:
    cairo_today = get_cairo_today()

    existing_vote = db.scalar(
        select(DailyChatSessionVote).where(
            DailyChatSessionVote.session_date == cairo_today,
            DailyChatSessionVote.user_id == current_user.id,
            DailyChatSessionVote.refunded.is_(False),
        )
    )
    if existing_vote is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لقد قمت بالتصويت لغرفة اليوم بالفعل.",
        )

    # Deduct 0.5 coins (50 points)
    tx_id = f"chat_vote_{cairo_today.isoformat()}_{current_user.id}"
    try:
        debit_points(
            db,
            user_id=current_user.id,
            amount_points=VOTE_COST_POINTS,
            transaction_id=tx_id,
            entry_type="trading_chat_vote",
            details={"session_date": cairo_today.isoformat(), "coins": 0.5},
        )
    except InsufficientBalanceError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رصيد العملات غير كافٍ. تكلفة التصويت 0.5 عملة.",
        )

    vote = DailyChatSessionVote(
        user_id=current_user.id,
        session_date=cairo_today,
        coins_paid=0.5,
    )
    db.add(vote)
    db.commit()

    votes_count = db.scalar(
        select(func.count(DailyChatSessionVote.id)).where(
            DailyChatSessionVote.session_date == cairo_today,
            DailyChatSessionVote.refunded.is_(False),
        )
    ) or 0

    is_unlocked = votes_count >= VOTE_TARGET

    return VoteRequestResponse(
        success=True,
        message="تم تصويتك لفتح الغرفة بنجاح!",
        votes_count=votes_count,
        is_unlocked=is_unlocked,
    )


@router.get("/messages", response_model=list[ChatMessageItem])
def get_chat_messages(
    db: DatabaseSession,
    current_user: CurrentUser,
) -> list[ChatMessageItem]:
    cairo_now = get_cairo_now()
    cairo_today = cairo_now.date()

    votes_count = db.scalar(
        select(func.count(DailyChatSessionVote.id)).where(
            DailyChatSessionVote.session_date == cairo_today,
            DailyChatSessionVote.refunded.is_(False),
        )
    ) or 0

    if votes_count < VOTE_TARGET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="غرفة التداول المباشر لم تصل إلى 40 صوتًا لليوم بعد.",
        )

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

    votes_count = db.scalar(
        select(func.count(DailyChatSessionVote.id)).where(
            DailyChatSessionVote.session_date == cairo_today,
            DailyChatSessionVote.refunded.is_(False),
        )
    ) or 0

    if votes_count < VOTE_TARGET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="الغرفة مغلقة حتى الوصول إلى 40 صوتًا.",
        )

    if not is_cairo_trading_hours(cairo_now):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="جلسة التداول المباشر متاحة فقط بين الساعة 9:00 صباحًا و 3:00 مساءً بتوقيت مصر.",
        )

    author_name = current_user.display_name or current_user.full_name or "متداول"

    msg = DailyChatMessage(
        user_id=current_user.id,
        session_date=cairo_today,
        user_name=author_name,
        content=body.content.trim(),
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
