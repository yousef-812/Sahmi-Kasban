import pytest
from unittest.mock import AsyncMock

from app.api.routes.ai_copilot import AiCopilotQueryRequest, query_ai_copilot
from app.models import User
from fastapi import HTTPException


@pytest.mark.anyio
async def test_ai_copilot_referral_gate(db_session):
    u = User(
        email="copilot_user@example.com",
        password_hash="hash",
        display_name="Copilot User",
    )
    db_session.add(u)
    db_session.commit()

    mock_ai = AsyncMock()

    # User has 0 referrals (< 5) -> Should raise 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        await query_ai_copilot(
            body=AiCopilotQueryRequest(question="ما هو سعر دخول سهم فوري؟"),
            db=db_session,
            current_user=u,
            ai_service=mock_ai,
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["error_code"] == "REFERRAL_GATE_LOCKED"
    assert exc_info.value.detail["current"] == 0
    assert exc_info.value.detail["required"] == 5


@pytest.mark.anyio
async def test_ai_copilot_admin_bypass(db_session, monkeypatch):
    monkeypatch.setenv("ADMIN_EMAILS", "yousefftaalip@gmail.com,yousrytalip@gmail.com")
    u = User(
        email="yousrytalip@gmail.com",
        password_hash="hash",
        display_name="Admin User",
    )
    db_session.add(u)
    db_session.commit()

    mock_ai = AsyncMock()
    mock_ai.generate_market_insight.return_value = "تحليل السهم رائع وجاهز للشراء."

    res = await query_ai_copilot(
        body=AiCopilotQueryRequest(question="ما هو تحليل سهم التجاري الدولي؟"),
        db=db_session,
        current_user=u,
        ai_service=mock_ai,
    )

    assert res.answer == "تحليل السهم رائع وجاهز للشراء."
    assert res.coins_deducted == 0.0
