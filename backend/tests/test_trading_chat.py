from uuid import uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.trading_chat import (
    get_cairo_today,
    get_chat_messages,
    get_trading_chat_status,
    vote_to_open_chat,
)
from app.jobs.refund_failed_chat_votes import refund_failed_chat_votes_job
from app.models import DailyChatSessionVote, User, WalletAccount


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


def test_trading_chat_status_and_voting(db_session: Session) -> None:
    user = create_test_user(db_session, "trader1@test.com", coins=5.0)

    # 1. Get status
    status_resp = get_trading_chat_status(db=db_session, current_user=user)
    assert status_resp.votes_count == 0
    assert status_resp.is_unlocked is False
    assert status_resp.has_voted is False

    # 2. Vote
    vote_resp = vote_to_open_chat(db=db_session, current_user=user)
    assert vote_resp.success is True
    assert vote_resp.votes_count == 1

    # Check updated wallet balance (5.0 - 0.5 = 4.5 coins => 450 points)
    wallet = db_session.scalar(select(WalletAccount).where(WalletAccount.user_id == user.id))
    assert wallet.balance_points == 450

    # 3. Double voting fails
    with pytest.raises(HTTPException) as exc:
        vote_to_open_chat(db=db_session, current_user=user)
    assert exc.value.status_code == 400


def test_chat_messages_locked_until_40_votes(db_session: Session) -> None:
    user = create_test_user(db_session, "trader2@test.com", coins=5.0)

    # Message fetch attempt fails when votes < 40
    with pytest.raises(HTTPException) as exc:
        get_chat_messages(db=db_session, current_user=user)
    assert exc.value.status_code == 403


def test_refund_cron_job(db_session: Session) -> None:
    user = create_test_user(db_session, "trader3@test.com", coins=1.0)
    today = get_cairo_today()

    # Create 1 vote
    vote = DailyChatSessionVote(
        id=uuid4(),
        user_id=user.id,
        session_date=today,
        coins_paid=0.5,
        refunded=False,
    )
    db_session.add(vote)

    # Deduct 50 points manually to simulate vote payment
    wallet = db_session.scalar(select(WalletAccount).where(WalletAccount.user_id == user.id))
    wallet.balance_points -= 50
    db_session.commit()

    assert wallet.balance_points == 50

    # Execute refund job since total votes (1) < 40
    result = refund_failed_chat_votes_job(db_session, target_date=today)
    assert result["status"] == "refunded"
    assert result["refunded_votes_count"] == 1

    db_session.refresh(wallet)
    assert wallet.balance_points == 100  # Refunded 50 points back to 100 (1.0 coin)
