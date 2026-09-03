from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import User, WalletAccount


def _seed_user(db: Session) -> tuple[User, dict[str, str]]:
    user = User(
        email="investor-api@example.com",
        password_hash="hashed-password",
        display_name="Investor User",
        avatar_key="avatar_01",
        status="active",
        email_verified=True,
        auth_version=0,
    )
    db.add(user)
    db.flush()
    db.add(WalletAccount(user_id=user.id, balance_points=500))
    db.commit()
    token, _ = create_access_token(user.id, user.auth_version)
    return user, {"Authorization": f"Bearer {token}"}


def test_investment_report_endpoints(client: TestClient, db_session: Session):
    _, headers = _seed_user(db_session)

    mock_rankings = [
        {
            "ticker": "FWRY",
            "company_name": "فوري لتكنولوجيا البنوك",
            "sector": "تكنولوجيا",
            "current_price": 20.0,
            "investment_score": 92.5,
            "pe_ratio": 12.0,
            "pb_ratio": 2.5,
            "dividend_yield_pct": 8.5,
            "roe_pct": 24.0,
            "fair_value": 30.0,
            "margin_of_safety_pct": 50.0,
            "investment_category": "dividend",
            "strengths": ["توزيعات نقدية قوية", "مكرر ربحية متوازن"],
            "risks": [],
        }
    ]

    with patch(
        "app.api.routes.reports.get_egx_investment_rankings",
        new=AsyncMock(return_value=mock_rankings),
    ):
        # 1. Preview
        preview_res = client.get("/api/v1/market/reports/investment/preview", headers=headers)
        assert preview_res.status_code == 200
        preview_data = preview_res.json()
        assert preview_data["report_type"] == "investment"
        assert preview_data["item_count"] == 1
        assert preview_data["unlocked"] is True

        # 2. Latest
        latest_res = client.get("/api/v1/market/reports/investment/latest", headers=headers)
        assert latest_res.status_code == 200
        latest_data = latest_res.json()
        assert latest_data["report_type"] == "investment"
        assert len(latest_data["items"]) == 1
        item = latest_data["items"][0]
        assert item["ticker"] == "FWRY"
        assert item["score"] == 92.5
        assert item["payload"]["fair_value"] == 30.0
        assert item["payload"]["margin_of_safety_pct"] == 50.0
        assert item["payload"]["investment_category"] == "dividend"
