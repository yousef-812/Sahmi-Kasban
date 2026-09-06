from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.routes.admin_ai_failures import clear_user_ai_cooldown, list_ai_failures
from app.api.routes.ai_copilot import AiCopilotQueryRequest, query_ai_copilot
from app.models import AiFailureLog, User, WalletAccount
from app.services.wallet import credit_points


def test_ai_copilot_failure_logs_and_sets_cooldown(db_session):
    u = User(
        email="failing_ai_user@example.com",
        password_hash="hash",
        display_name="Failing User",
    )
    db_session.add(u)
    db_session.flush()

    wallet = WalletAccount(user_id=u.id, balance_points=100)  # 1 coin
    db_session.add(wallet)

    # 5 referrals to bypass gate
    for i in range(5):
        ref = User(
            email=f"ref_{i}@example.com",
            password_hash="hash",
            display_name=f"Ref {i}",
            referred_by_id=u.id,
        )
        db_session.add(ref)

    db_session.commit()

    mock_ai = MagicMock()
    mock_ai.generate_market_insight.side_effect = RuntimeError("Gemini API connection timeout")

    # 1. Query should fail, log to AiFailureLog, set 1-hour cooldown, and not debit points
    with pytest.raises(HTTPException) as exc_info:
        query_ai_copilot(
            body=AiCopilotQueryRequest(ticker="COMI", question="ما هو اتجاه سهم البنك التجاري؟"),
            db=db_session,
            current_user=u,
            ai_service=mock_ai,
        )

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail["error_code"] == "AI_SERVICE_FAILURE"

    # Verify wallet balance is unchanged (still 100 points)
    db_session.refresh(wallet)
    assert wallet.balance_points == 100

    # Verify cooldown set on user
    db_session.refresh(u)
    assert u.ai_cooldown_until is not None
    cooldown = u.ai_cooldown_until.replace(tzinfo=UTC) if u.ai_cooldown_until.tzinfo is None else u.ai_cooldown_until
    assert cooldown > datetime.now(UTC)

    # Verify failure log in DB
    logs = db_session.query(AiFailureLog).filter_by(user_id=u.id).all()
    assert len(logs) == 1
    assert logs[0].ticker == "COMI"
    assert "Gemini API connection timeout" in logs[0].error_message

    # 2. Subsequent query during cooldown should be blocked with 403
    with pytest.raises(HTTPException) as exc_cooldown:
        query_ai_copilot(
            body=AiCopilotQueryRequest(ticker="COMI", question="سؤال ثاني"),
            db=db_session,
            current_user=u,
            ai_service=mock_ai,
        )

    assert exc_cooldown.value.status_code == 403
    assert exc_cooldown.value.detail["error_code"] == "AI_COOLDOWN_ACTIVE"

    # 3. Admin clears cooldown
    admin_u = User(email="admin@example.com", password_hash="hash", display_name="Admin")
    db_session.add(admin_u)
    db_session.commit()

    resp = clear_user_ai_cooldown(user_id=u.id, db=db_session, admin=admin_u)
    assert resp.success is True

    db_session.refresh(u)
    assert u.ai_cooldown_until is None
