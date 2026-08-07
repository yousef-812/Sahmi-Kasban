from datetime import UTC, date, datetime

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import (
    MarketReport,
    MarketReportItem,
    MarketReportUnlock,
    User,
    WalletAccount,
    WalletEntry,
)


def _seed_user(db: Session, *, balance_points: int = 300) -> tuple[User, dict[str, str]]:
    user = User(
        email="report-api@example.com",
        password_hash="hashed-password",
        display_name="Report User",
        avatar_key="avatar_01",
        status="active",
        email_verified=True,
        auth_version=0,
    )
    db.add(user)
    db.flush()
    db.add(WalletAccount(user_id=user.id, balance_points=balance_points))
    db.commit()
    token, _ = create_access_token(user.id, user.auth_version)
    return user, {"Authorization": f"Bearer {token}"}


def _seed_report(db: Session, *, item_count: int = 10) -> MarketReport:
    report = MarketReport(
        target_session_date=date(2026, 7, 27),
        status="complete",
        generated_at=datetime(2026, 7, 26, 14, 15, tzinfo=UTC),
        source_snapshot={"source_session_date": "2026-07-26"},
        market_summary={
            "title": "الأسهم الأعلى تقييمًا وفق التحليل الآلي للجلسة القادمة",
            "eligible_count": 20,
        },
    )
    db.add(report)
    db.flush()
    for rank in range(1, item_count + 1):
        db.add(
            MarketReportItem(
                report_id=report.id,
                ticker=f"T{rank:02d}",
                rank=rank,
                score_bp=9_000 - rank,
                payload={"ticker": f"T{rank:02d}", "rank": rank},
            )
        )
    db.commit()
    return report


def test_preview_hides_items_until_report_is_unlocked(
    client: TestClient,
    db_session: Session,
) -> None:
    user, headers = _seed_user(db_session)
    report = _seed_report(db_session)

    preview = client.get("/api/v1/market/reports/latest/preview", headers=headers)
    assert preview.status_code == 200
    preview_payload = preview.json()
    assert preview_payload["report_id"] == str(report.id)
    assert preview_payload["item_count"] == 10
    assert preview_payload["unlocked"] is False
    assert preview_payload["unlock_cost_points"] == 100
    assert "items" not in preview_payload

    locked = client.get(f"/api/v1/market/reports/{report.id}", headers=headers)
    assert locked.status_code == 402

    first_unlock = client.post(
        f"/api/v1/market/reports/{report.id}/unlock",
        headers=headers,
    )
    assert first_unlock.status_code == 200
    first_payload = first_unlock.json()
    assert first_payload["charged_points"] == 100
    assert first_payload["balance_points"] == 200
    assert len(first_payload["report"]["items"]) == 10
    assert first_payload["report"]["extended_items"] == []

    second_unlock = client.post(
        f"/api/v1/market/reports/{report.id}/unlock",
        headers=headers,
    )
    assert second_unlock.status_code == 200
    assert second_unlock.json()["charged_points"] == 0
    assert second_unlock.json()["balance_points"] == 200

    full_report = client.get(
        f"/api/v1/market/reports/{report.id}",
        headers=headers,
    )
    assert full_report.status_code == 200
    assert len(full_report.json()["items"]) == 10
    assert db_session.scalar(select(func.count(MarketReportUnlock.id))) == 1
    assert (
        db_session.scalar(
            select(func.count(WalletEntry.id)).where(
                WalletEntry.user_id == user.id,
                WalletEntry.entry_type == "market_report_debit",
            )
        )
        == 1
    )


def test_incomplete_report_is_not_charged(
    client: TestClient,
    db_session: Session,
) -> None:
    user, headers = _seed_user(db_session)
    report = _seed_report(db_session, item_count=9)

    response = client.post(
        f"/api/v1/market/reports/{report.id}/unlock",
        headers=headers,
    )

    assert response.status_code == 409
    account = db_session.scalar(
        select(WalletAccount).where(WalletAccount.user_id == user.id)
    )
    assert account is not None
    assert account.balance_points == 300
    assert db_session.scalar(select(func.count(MarketReportUnlock.id))) == 0
    assert db_session.scalar(select(func.count(WalletEntry.id))) == 0


def test_report_response_includes_extended_items(
    client: TestClient,
    db_session: Session,
) -> None:
    user, headers = _seed_user(db_session)
    report = _seed_report(db_session)
    report.extended_universe = {
        "top_size": 10,
        "stored_count": 1,
        "entries": [
            {
                "ticker": "EXT1",
                "rank": 11,
                "score": 74.5,
                "signal": "BUY",
                "opportunity_tier": "conditional_buy",
                "elite_profile": "none",
                "elite": False,
                "decision": "شراء مشروط",
                "price_at_analysis": 22.5,
                "confidence": 66.0,
                "qualified": True,
                "trade_plan": {
                    "entry": 22.5,
                    "stop_loss": 21.0,
                    "target_1": 24.5,
                    "target_2": 26.0,
                    "reward_risk_1": 1.8,
                },
                "explanation": "فرصة قوية بشروط المخاطر.",
                "explanation_source": "deterministic",
                "selection_rank": 11,
                "top_fraction_pct": 8.8,
                "eligible_universe_size": 125,
            }
        ],
    }
    db_session.commit()

    unlocked = client.post(
        f"/api/v1/market/reports/{report.id}/unlock",
        headers=headers,
    )
    assert unlocked.status_code == 200
    body = unlocked.json()["report"]
    assert len(body["items"]) == 10
    assert len(body["extended_items"]) == 1
    extended = body["extended_items"][0]
    assert extended["ticker"] == "EXT1"
    assert extended["rank"] == 11
    assert extended["score"] == 74.5
    assert extended["payload"]["opportunity_tier"] == "conditional_buy"
    assert extended["payload"]["trade_plan"]["entry"] == 22.5
