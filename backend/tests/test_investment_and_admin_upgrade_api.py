from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import Subscription, User, WalletAccount


def _seed_user(db: Session, *, is_admin: bool = False) -> tuple[User, dict[str, str]]:
    email = "admin-test@example.com" if is_admin else "user-test@example.com"
    user = User(
        email=email,
        password_hash="hashed-password",
        display_name="Admin Test" if is_admin else "User Test",
        avatar_key="avatar_01",
        status="active",
        email_verified=True,
        auth_version=0,
    )
    db.add(user)
    db.flush()
    db.add(WalletAccount(user_id=user.id, balance_points=1000))
    db.commit()
    token, _ = create_access_token(user.id, user.auth_version)
    return user, {"Authorization": f"Bearer {token}"}


def test_single_stock_investment_analysis_and_comparison(client: TestClient, db_session: Session):
    user, headers = _seed_user(db_session)

    mock_metric = {
        "ticker": "COMI",
        "company_name": "البنك التجاري الدولي",
        "sector": "بنوك",
        "current_price": 85.0,
        "investment_score": 88.0,
        "pe_ratio": 7.5,
        "pb_ratio": 1.8,
        "dividend_yield_pct": 5.2,
        "roe_pct": 28.0,
        "fair_value": 110.0,
        "margin_of_safety_pct": 29.4,
        "investment_category": "value",
        "strengths": ["عائد حقوق ملكية ممتاز", "مكرر ربحية جذاب"],
        "risks": [],
    }

    with patch(
        "app.api.routes.market.get_stock_investment_metric",
        new=AsyncMock(return_value=mock_metric),
    ):
        # 1. Single stock investment endpoint
        res = client.get("/api/v1/stocks/COMI/investment", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["ticker"] == "COMI"
        assert data["fair_value"] == 110.0
        assert data["margin_of_safety_pct"] == 29.4
        assert data["pe_ratio"] == 7.5

    with patch(
        "app.api.routes.market.compare_stocks_investment",
        new=AsyncMock(
            return_value={
                "items": [mock_metric],
                "best_ticker": "COMI",
                "summary": "تتصدر شركة البنك التجاري الدولي المقارنة",
            }
        ),
    ):
        # 2. Stock investment comparison endpoint
        comp_res = client.post(
            "/api/v1/market/comparisons/investment",
            json={"tickers": ["COMI", "FWRY"]},
            headers=headers,
        )
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert comp_data["best_ticker"] == "COMI"
        assert len(comp_data["items"]) == 1


def test_admin_regenerate_investment_and_upgrade_plan(client: TestClient, db_session: Session):
    admin_user, admin_headers = _seed_user(db_session, is_admin=True)
    target_user, _ = _seed_user(db_session, is_admin=False)

    with (
        patch("app.api.dependencies.is_admin_email", return_value=True),
        patch(
            "app.market_data.fundamental.get_egx_investment_rankings",
            new=AsyncMock(return_value=[{"ticker": "COMI"}]),
        ),
    ):
        # 1. Regenerate investment report
        regen_res = client.post(
            "/api/v1/admin/operations/reports/investment/regenerate",
            headers=admin_headers,
        )
        assert regen_res.status_code == 200
        assert regen_res.json()["status"] == "success"

        # 2. Upgrade user plan manually
        upgrade_res = client.post(
            f"/api/v1/admin/operations/users/{target_user.id}/upgrade-plan",
            json={
                "plan_code": "pro",
                "duration_days": 90,
                "bonus_points": 500,
            },
            headers=admin_headers,
        )
        assert upgrade_res.status_code == 200, upgrade_res.text
        upgrade_data = upgrade_res.json()
        assert upgrade_data["user_id"] == str(target_user.id)
        assert upgrade_data["plan_code"] == "pro"
        assert upgrade_data["weekly_points"] == 15_000
        assert upgrade_data["ads_enabled"] is False
        assert upgrade_data["expires_at"] is not None

        # Verify in DB
        sub = db_session.query(Subscription).filter_by(user_id=target_user.id, status="active").first()
        assert sub is not None
        assert sub.plan_code == "pro"
