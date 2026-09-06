from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.routes.trading_chat import get_cairo_today
from app.jobs.refund_failed_chat_votes import refund_failed_chat_votes_job
from app.models import DailyChatSessionVote, User, WalletAccount
from app.services.wallet import credit_points


def create_test_user(db: Session, email: str, coins: float = 10.0) -> User:
    user = User(
        id=uuid4(),
        email=email,
        full_name="Test Trader",
        hashed_password="hash",
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


def test_trading_chat_status_and_voting(client: TestClient, db_session: Session) -> None:
    user = create_test_user(db_session, "trader1@test.com", coins=5.0)

    # 1. Get status (unauthenticated or as current user)
    client.force_login(user)
    resp = client.get("/api/v1/trading-chat/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["votes_count"] == 0
    assert data["is_unlocked"] is False
    assert data["has_voted"] is False

    # 2. Vote
    resp_vote = client.post("/api/v1/trading-chat/vote")
    assert resp_vote.status_code == 200
    vote_data = resp_vote.json()
    assert vote_data["success"] is True
    assert vote_data["votes_count"] == 1

    # Check updated wallet balance (5.0 - 0.5 = 4.5 coins => 450 points)
    wallet = db_session.scalar(
        db_session.query(WalletAccount).where(WalletAccount.user_id == user.id)
    )
    assert wallet.balance_points == 450

    # 3. Double voting fails
    resp_double = client.post("/api/v1/trading-chat/vote")
    assert resp_double.status_code == 400


def test_chat_messages_locked_until_40_votes(client: TestClient, db_session: Session) -> None:
    user = create_test_user(db_session, "trader2@test.com", coins=5.0)
    client.force_login(user)

    # Message post attempt fails when votes < 40
    resp = client.get("/api/v1/trading-chat/messages")
    assert resp.status_code == 403


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
    wallet = db_session.scalar(
        db_session.query(WalletAccount).where(WalletAccount.user_id == user.id)
    )
    wallet.balance_points -= 50
    db_session.commit()

    assert wallet.balance_points == 50

    # Execute refund job since total votes (1) < 40
    result = refund_failed_chat_votes_job(db_session, target_date=today)
    assert result["status"] == "refunded"
    assert result["refunded_votes_count"] == 1

    db_session.refresh(wallet)
    assert wallet.balance_points == 100  # Refunded 50 points back to 100 (1.0 coin)
