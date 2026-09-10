from uuid import uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.trading_chat import (
    get_cairo_today,
    get_chat_messages,
    get_trading_chat_status,
    post_chat_message,
    is_chat_active_now,
    PostChatMessageRequest,
)
from app.jobs.refund_failed_chat_votes import refund_failed_chat_votes_job
from app.models import DailyChatMessage, DailyChatSessionVote, User, WalletAccount


def create_test_user(db: Session, email: str, coins: float = 10.0) -> User:
    user = User(
        id=uuid4(),
        email=email,
        display_name="Test Trader",
        password_hash="hash",
    )
    db.add(user)
    db.flush()

    wallet = WalletAccount(
        user_id=user.id,
        balance_points=int(coins * 100),
    )
    db.add(wallet)
    db.commit()
    db.refresh(user)
    return user


def test_trading_chat_status(db_session: Session) -> None:
    user = create_test_user(db_session, "trader1@test.com", coins=5.0)

    status_resp = get_trading_chat_status(db=db_session, current_user=user)
    assert status_resp.session_date == get_cairo_today().isoformat()
    assert isinstance(status_resp.is_session_open, bool)
    assert status_resp.chat_start_hour == 10
    assert status_resp.chat_end_hour == 14
    assert status_resp.chat_end_minute == 30


def test_chat_messages_returns_list(db_session: Session) -> None:
    user = create_test_user(db_session, "trader2@test.com", coins=5.0)

    messages = get_chat_messages(db=db_session, current_user=user)
    assert isinstance(messages, list)


def test_refund_cron_job_is_noop(db_session: Session) -> None:
    result = refund_failed_chat_votes_job(db_session)
    assert result["status"] == "no_voting_system"
    assert result["refunded_votes_count"] == 0
