from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import ScannerSnapshot, User, WalletAccount, WalletEntry


def _seed_user(db: Session, *, balance_points: int = 1000) -> tuple[User, dict[str, str]]:
    user = User(
        email="sector-api@example.com",
        password_hash="hashed-password",
        display_name="Sector User",
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


def _add_technical_snapshot(
    db: Session,
    *,
    symbol: str,
    sector: str,
    score: float,
    rating: str,
    name_ar: str | None = None,
    performance_20d: float | None = None,
    as_of: datetime | None = None,
) -> None:
    payload: dict = {
        "symbol": symbol,
        "sector": sector,
        "timeframe": "1D",
        "technicalScore": score,
        "technicalRating": rating,
        "atr14": 1.5,
        "relativeVolume20": 1.8,
        "rsi14": 61.0,
        "performance20d": performance_20d,
    }
    if name_ar is not None:
        payload["nameAr"] = name_ar
    db.add(
        ScannerSnapshot(
            kind="technical",
            symbol=symbol,
            timeframe="1D",
            as_of=as_of or datetime.now(UTC),
            score=score,
            rating=rating,
            payload=payload,
        )
    )
    db.commit()


def test_sector_leaderboard_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/reports/sectors/banking/leaderboard").status_code == 401


def test_sector_leaderboard_unknown_sector_returns_404(
    client: TestClient, db_session: Session
) -> None:
    _user, headers = _seed_user(db_session)

    response = client.get("/api/v1/reports/sectors/invalid_sector/leaderboard", headers=headers)

    assert response.status_code == 404
    assert "القطاعات المتاحة" in response.json()["detail"]


def test_sector_leaderboard_computes_ranking_from_scanner_snapshots(
    client: TestClient, db_session: Session
) -> None:
    _user, headers = _seed_user(db_session, balance_points=1000)
    base = datetime(2026, 7, 25, 10, tzinfo=UTC)
    _add_technical_snapshot(
        db_session,
        symbol="COMI",
        sector="البنوك",
        score=92.5,
        rating="buy",
        name_ar="البنك التجاري الدولي",
        performance_20d=4.0,
        as_of=base,
    )
    _add_technical_snapshot(
        db_session,
        symbol="CIEB",
        sector="البنوك",
        score=71.0,
        rating="buy",
        performance_20d=2.0,
        as_of=base,
    )
    _add_technical_snapshot(
        db_session,
        symbol="HDBK",
        sector="البنوك",
        score=-55.0,
        rating="sell",
        performance_20d=-3.0,
        as_of=base,
    )
    # Same score as CIEB -> ticker ascending is the tiebreak.
    _add_technical_snapshot(
        db_session,
        symbol="ADIB",
        sector="البنوك",
        score=71.0,
        rating="buy",
        as_of=base,
    )
    # A symbol from another sector must not leak into the banking leaderboard.
    _add_technical_snapshot(
        db_session,
        symbol="TMGH",
        sector="العقارات",
        score=99.0,
        rating="buy",
        as_of=base,
    )

    response = client.get("/api/v1/reports/sectors/banking/leaderboard", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["sector_code"] == "banking"
    assert body["sector_name"] == "قطاع البنوك"
    assert body["leader_ticker"] == "COMI"
    assert body["coins_deducted"] == 2.0
    assert body["degraded"] is False

    assert [item["ticker"] for item in body["items"]] == ["COMI", "ADIB", "CIEB", "HDBK"]
    first = body["items"][0]
    assert first["rank"] == 1
    assert first["score"] == 92.5
    assert first["rating"] == "buy"
    assert first["signal"] == "شراء"
    assert first["company_name"] == "البنك التجاري الدولي"
    assert first["atr"] == 1.5
    assert first["relative_volume"] == 1.8
    assert first["rsi14"] == 61.0
    assert first["performance_20d_pct"] == 4.0
    assert first["as_of"] == base.isoformat()
    assert body["items"][3]["signal"] == "بيع"

    summary = body["summary"]
    assert summary["scanner_kind"] == "technical"
    assert summary["symbol_count"] == 4
    assert summary["average_score"] == round((92.5 + 71.0 + 71.0 - 55.0) / 4, 2)
    assert summary["buy_count"] == 3
    assert summary["sell_count"] == 1
    assert summary["neutral_count"] == 0
    assert summary["best_ticker"] == "COMI"
    assert summary["worst_ticker"] == "HDBK"
    quality = summary["quality"]
    assert quality["sector_name"] == "البنوك"
    assert quality["score"] == summary["average_score"]


def test_sector_leaderboard_debits_exactly_two_coins(
    client: TestClient, db_session: Session
) -> None:
    user, headers = _seed_user(db_session, balance_points=1000)

    response = client.get("/api/v1/reports/sectors/banking/leaderboard", headers=headers)

    assert response.status_code == 200
    account = db_session.scalar(select(WalletAccount).where(WalletAccount.user_id == user.id))
    assert account is not None
    assert account.balance_points == 800
    entry = db_session.scalar(
        select(WalletEntry).where(WalletEntry.user_id == user.id, WalletEntry.amount_points == -200)
    )
    assert entry is not None
    assert entry.entry_type == "sector_report_purchase"
    assert entry.details == {"sector_code": "banking"}


def test_sector_leaderboard_insufficient_balance_returns_400(
    client: TestClient, db_session: Session
) -> None:
    user, headers = _seed_user(db_session, balance_points=100)

    response = client.get("/api/v1/reports/sectors/banking/leaderboard", headers=headers)

    assert response.status_code == 400
    account = db_session.scalar(select(WalletAccount).where(WalletAccount.user_id == user.id))
    assert account is not None
    assert account.balance_points == 100
    assert db_session.scalars(select(WalletEntry).where(WalletEntry.user_id == user.id)).all() == []


def test_sector_leaderboard_degrades_when_snapshots_missing(
    client: TestClient, db_session: Session
) -> None:
    user, headers = _seed_user(db_session, balance_points=1000)

    response = client.get("/api/v1/reports/sectors/banking/leaderboard", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["degraded"] is True
    assert body["items"] == []
    assert body["leader_ticker"] == ""
    assert body["summary"]["symbol_count"] == 0
    assert body["summary"]["average_score"] is None
    assert body["summary"]["best_ticker"] is None
    assert body["summary"]["worst_ticker"] is None
    assert body["summary"]["quality"] is None
    # The purchase is still charged: the debit happens before generation, as before.
    account = db_session.scalar(select(WalletAccount).where(WalletAccount.user_id == user.id))
    assert account is not None
    assert account.balance_points == 800


def test_sector_leaderboard_neutral_symbol_labelled_arabic(
    client: TestClient, db_session: Session
) -> None:
    _user, headers = _seed_user(db_session, balance_points=1000)
    _add_technical_snapshot(
        db_session,
        symbol="COMI",
        sector="البنوك",
        score=5.0,
        rating="neutral",
    )

    response = client.get("/api/v1/reports/sectors/banking/leaderboard", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["signal"] == "محايد"
    assert body["summary"]["neutral_count"] == 1
