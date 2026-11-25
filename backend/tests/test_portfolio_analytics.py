from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.market_data.types import CandleSeries
from app.models import User, WatchlistItem
from app.services import portfolio_analytics as portfolio_service
from app.services.signal_lifecycle import close_signal, open_signal

PASSWORD = "StrongPass123"


def _register_and_login(client: TestClient, fake_email_service, *, email: str) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "display_name": "Portfolio Tester"},
    )
    assert registered.status_code == 201
    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"token": fake_email_service.verification_tokens[email]},
    )
    assert verified.status_code == 200
    login = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _user_id(db_session: Session, email: str):
    return db_session.query(User).filter(User.email == email).one().id


def _closes(start: float, step: float, sessions: int = 12) -> list[float]:
    return [start + step * index for index in range(sessions)]


def _mirrored_closes(closes: list[float], base: float = 100.0) -> list[float]:
    """Closes whose daily returns are the exact negation of ``closes`` returns."""
    mirrored = [base]
    for index in range(1, len(closes)):
        daily_return = closes[index] / closes[index - 1] - 1.0
        mirrored.append(mirrored[-1] * (1.0 - daily_return))
    return mirrored


def _make_series(ticker: str, closes: list[float]) -> CandleSeries:
    now = datetime.now(UTC)
    candles = tuple(
        {
            "timestamp": (datetime(2025, 6, 1, tzinfo=UTC) + timedelta(days=index)).isoformat(),
            "open": price,
            "high": price,
            "low": price,
            "close": price,
            "volume": 1000.0,
        }
        for index, price in enumerate(closes)
    )
    return CandleSeries(
        ticker=ticker,
        provider="stub",
        interval="1d",
        period="1y",
        fetched_at=now,
        data_as_of=now,
        fingerprint=f"stub-{ticker}",
        candles=candles,
    )


def _stub_history(closes_by_ticker: dict[str, list[float]]):
    async def _stub(db, provider, ticker, **kwargs):
        closes = closes_by_ticker.get(ticker)
        if closes is None:
            raise RuntimeError(f"No stub candles for {ticker}")
        return _make_series(ticker, closes), True

    return _stub


def test_portfolio_analytics_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/portfolio/analytics").status_code == 401


def test_empty_portfolio(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    headers = _register_and_login(client, fake_email_service, email="portfolio-empty@example.com")
    monkeypatch.setattr(portfolio_service, "get_cached_or_fresh_history", _stub_history({}))

    response = client.get("/api/v1/portfolio/analytics", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["position_count"] == 0
    assert body["positions"] == []
    assert body["correlation"]["tickers"] == []
    assert body["correlation"]["matrix"] == {}
    assert body["diversification"]["herfindahl"] == 0.0
    assert body["diversification"]["effective_positions"] == 0.0
    assert body["diversification"]["concentration_flag"] is False
    assert body["sector_exposure"] == {}
    assert any("No open positions" in warning for warning in body["warnings"])


def test_single_position_weights_price_and_sector(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    email = "portfolio-single@example.com"
    headers = _register_and_login(client, fake_email_service, email=email)
    open_signal(
        db_session,
        ticker="COMI",
        direction="long",
        entry=100.0,
        stop=95.0,
        targets=(105.0, None, None),
        source="manual",
        user_id=_user_id(db_session, email),
    )
    monkeypatch.setattr(
        portfolio_service, "get_cached_or_fresh_history", _stub_history({"COMI": _closes(100, 1)})
    )

    body = client.get("/api/v1/portfolio/analytics", headers=headers).json()
    assert body["position_count"] == 1
    position = body["positions"][0]
    assert position["ticker"] == "COMI"
    assert position["direction"] == "long"
    assert position["entry"] == 100.0
    assert position["stop"] == 95.0
    assert position["current_price"] == 111.0
    assert position["weight"] == 1.0
    assert position["sector"] == "البنوك"
    assert position["unrealized_pct"] == 11.0

    assert body["correlation"]["tickers"] == ["COMI"]
    assert body["correlation"]["matrix"] == {"COMI": {"COMI": 1.0}}

    diversification = body["diversification"]
    assert diversification["herfindahl"] == 1.0
    assert diversification["effective_positions"] == 1.0
    assert diversification["concentration_flag"] is True
    assert diversification["concentration_threshold"] == 0.4

    assert body["sector_exposure"] == {"البنوك": 1.0}
    assert any("COMI" in warning and "concentration" in warning for warning in body["warnings"])


def test_two_positions_correlation_matrix_is_symmetric(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    email = "portfolio-pair@example.com"
    headers = _register_and_login(client, fake_email_service, email=email)
    user_id = _user_id(db_session, email)
    open_signal(
        db_session,
        ticker="COMI",
        direction="long",
        entry=80.0,
        stop=76.0,
        targets=(84.0, None, None),
        source="manual",
        user_id=user_id,
    )
    open_signal(
        db_session,
        ticker="TMGH",
        direction="long",
        entry=20.0,
        stop=19.0,
        targets=(21.0, None, None),
        source="manual",
        user_id=user_id,
    )
    comi_closes = _closes(100, 1)
    monkeypatch.setattr(
        portfolio_service,
        "get_cached_or_fresh_history",
        _stub_history({"COMI": comi_closes, "TMGH": _mirrored_closes(comi_closes)}),
    )

    body = client.get("/api/v1/portfolio/analytics", headers=headers).json()
    assert body["position_count"] == 2
    assert [item["ticker"] for item in body["positions"]] == ["COMI", "TMGH"]
    assert [item["weight"] for item in body["positions"]] == [0.8, 0.2]

    correlation = body["correlation"]
    assert correlation["tickers"] == ["COMI", "TMGH"]
    matrix = correlation["matrix"]
    assert matrix["COMI"]["COMI"] == 1.0
    assert matrix["TMGH"]["TMGH"] == 1.0
    assert matrix["COMI"]["TMGH"] == matrix["TMGH"]["COMI"]
    assert matrix["COMI"]["TMGH"] < -0.99

    diversification = body["diversification"]
    assert abs(diversification["herfindahl"] - (0.8**2 + 0.2**2)) < 1e-6
    assert diversification["concentration_flag"] is True
    assert any("COMI" in warning for warning in body["warnings"])


def test_identical_positions_are_perfectly_correlated(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    email = "portfolio-identical@example.com"
    headers = _register_and_login(client, fake_email_service, email=email)
    user_id = _user_id(db_session, email)
    for ticker in ("COMI", "TMGH"):
        open_signal(
            db_session,
            ticker=ticker,
            direction="long",
            entry=50.0,
            stop=48.0,
            targets=(52.0, None, None),
            source="manual",
            user_id=user_id,
        )
    closes = _closes(100, 2)
    monkeypatch.setattr(
        portfolio_service,
        "get_cached_or_fresh_history",
        _stub_history({"COMI": closes, "TMGH": list(closes)}),
    )

    body = client.get("/api/v1/portfolio/analytics", headers=headers).json()
    matrix = body["correlation"]["matrix"]
    assert matrix["COMI"]["TMGH"] == 1.0
    assert matrix["TMGH"]["COMI"] == 1.0


def test_sector_exposure_sums_to_one_and_same_sector_warning(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    email = "portfolio-sector@example.com"
    headers = _register_and_login(client, fake_email_service, email=email)
    user_id = _user_id(db_session, email)
    for ticker in ("COMI", "HDBK"):
        open_signal(
            db_session,
            ticker=ticker,
            direction="long",
            entry=50.0,
            stop=48.0,
            targets=(52.0, None, None),
            source="manual",
            user_id=user_id,
        )
    closes = _closes(100, 1)
    monkeypatch.setattr(
        portfolio_service,
        "get_cached_or_fresh_history",
        _stub_history({"COMI": closes, "HDBK": list(closes)}),
    )

    body = client.get("/api/v1/portfolio/analytics", headers=headers).json()
    assert body["sector_exposure"] == {"البنوك": 1.0}
    assert abs(sum(body["sector_exposure"].values()) - 1.0) < 1e-9
    assert any(
        "البنوك" in warning and "sector diversification is zero" in warning
        for warning in body["warnings"]
    )


def test_missing_price_data_falls_back_to_watchlist_and_warns(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    email = "portfolio-missing@example.com"
    headers = _register_and_login(client, fake_email_service, email=email)
    user_id = _user_id(db_session, email)
    open_signal(
        db_session,
        ticker="TMGH",
        direction="short",
        entry=60.0,
        stop=63.0,
        targets=(57.0, None, None),
        source="manual",
        user_id=user_id,
    )
    db_session.add(
        WatchlistItem(user_id=user_id, ticker="TMGH", last_price=Decimal("54"), notes={})
    )
    db_session.commit()
    monkeypatch.setattr(portfolio_service, "get_cached_or_fresh_history", _stub_history({}))

    body = client.get("/api/v1/portfolio/analytics", headers=headers).json()
    position = body["positions"][0]
    assert position["current_price"] == 54.0
    assert position["unrealized_pct"] == 10.0
    assert body["watchlist"]["tickers"] == ["TMGH"]
    assert any("No candle history available for TMGH" in warning for warning in body["warnings"])


def test_closed_and_expired_signals_are_not_positions(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    email = "portfolio-closed@example.com"
    headers = _register_and_login(client, fake_email_service, email=email)
    user_id = _user_id(db_session, email)
    signal = open_signal(
        db_session,
        ticker="COMI",
        direction="long",
        entry=100.0,
        stop=95.0,
        targets=(105.0, None, None),
        source="manual",
        user_id=user_id,
    )
    close_signal(db_session, signal, reason="manual close", price=104.0)
    monkeypatch.setattr(portfolio_service, "get_cached_or_fresh_history", _stub_history({}))

    body = client.get("/api/v1/portfolio/analytics", headers=headers).json()
    assert body["position_count"] == 0


def test_analytics_are_scoped_to_the_calling_user(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    owner_email = "portfolio-owner@example.com"
    _register_and_login(client, fake_email_service, email=owner_email)
    open_signal(
        db_session,
        ticker="COMI",
        direction="long",
        entry=100.0,
        stop=95.0,
        targets=(105.0, None, None),
        source="manual",
        user_id=_user_id(db_session, owner_email),
    )
    other_headers = _register_and_login(client, fake_email_service, email="portfolio-other@example.com")
    monkeypatch.setattr(
        portfolio_service,
        "get_cached_or_fresh_history",
        _stub_history({"COMI": _closes(100, 1)}),
    )

    body = client.get("/api/v1/portfolio/analytics", headers=other_headers).json()
    assert body["position_count"] == 0
    assert body["positions"] == []


def test_endpoint_response_shape(
    client: TestClient,
    fake_email_service,
    db_session: Session,
    monkeypatch,
) -> None:
    email = "portfolio-shape@example.com"
    headers = _register_and_login(client, fake_email_service, email=email)
    open_signal(
        db_session,
        ticker="COMI",
        direction="long",
        entry=100.0,
        stop=95.0,
        targets=(105.0, None, None),
        source="manual",
        user_id=_user_id(db_session, email),
    )
    monkeypatch.setattr(
        portfolio_service, "get_cached_or_fresh_history", _stub_history({"COMI": _closes(100, 1)})
    )

    response = client.get("/api/v1/portfolio/analytics", headers=headers)
    assert response.status_code == 200
    body = response.json()
    for key in (
        "as_of",
        "position_count",
        "positions",
        "correlation",
        "diversification",
        "sector_exposure",
        "watchlist",
        "warnings",
        "analytics_version",
    ):
        assert key in body
    for key in ("lookback_sessions", "min_observations", "tickers", "matrix"):
        assert key in body["correlation"]
    for key in ("herfindahl", "effective_positions", "concentration_flag", "concentration_threshold"):
        assert key in body["diversification"]
    for key in ("ticker", "direction", "entry", "stop", "current_price", "weight", "sector", "unrealized_pct"):
        assert key in body["positions"][0]
    assert body["as_of"].endswith("Z") or "+" in body["as_of"]
