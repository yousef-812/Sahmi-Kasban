import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.models import User
from app.api.routes.ai_copilot import query_ai_copilot, AiCopilotQueryRequest
from fastapi import HTTPException


def test_ai_copilot_referral_gate(db_session):
    u = User(
        email="copilot_user@example.com",
        password_hash="hash",
        display_name="Copilot User",
    )
    db_session.add(u)
    db_session.commit()

    mock_ai = MagicMock()

    # User has 0 referrals (< 5) -> Should raise 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        query_ai_copilot(
            body=AiCopilotQueryRequest(question="ما هو سعر دخول سهم فوري؟"),
            db=db_session,
            current_user=u,
            ai_service=mock_ai,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["error_code"] == "REFERRAL_GATE_LOCKED"
    assert exc_info.value.detail["current"] == 0
    assert exc_info.value.detail["required"] == 5


def test_ai_copilot_admin_bypass(db_session, monkeypatch):
    monkeypatch.setenv("ADMIN_EMAILS", "yousefftaalip@gmail.com,yousrytalip@gmail.com")
    u = User(
        email="yousrytalip@gmail.com",
        password_hash="hash",
        display_name="Admin User",
    )
    db_session.add(u)
    db_session.commit()

    mock_ai = MagicMock()
    mock_ai.generate_market_insight.return_value = "تحليل السهم رائع وجاهز للشراء."

    res = query_ai_copilot(
        body=AiCopilotQueryRequest(question="ما هو تحليل سهم التجاري الدولي؟"),
        db=db_session,
        current_user=u,
        ai_service=mock_ai,
    )

    assert res.answer == "تحليل السهم رائع وجاهز للشراء."
    assert res.coins_deducted == 0.0
