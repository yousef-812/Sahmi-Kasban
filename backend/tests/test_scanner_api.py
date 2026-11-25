from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.market_data.provider import get_market_data_provider
from app.market_data.types import CandleSeries, MarketDataUnavailableError
from app.models import ScannerSnapshot

PASSWORD = "StrongPass123"

ZIGZAG_START = datetime(2025, 9, 1, tzinfo=UTC)


def _zigzag_candles(count: int = 220) -> list[dict[str, object]]:
    candles: list[dict[str, object]] = []
    price = 100.0
    for index in range(count):
        price += 1.0 if index % 40 < 20 else -0.8
        candles.append(
            {
                "timestamp": (ZIGZAG_START + timedelta(days=index)).isoformat(),
                "open": round(price - 0.2, 6),
                "high": round(price + 0.7, 6),
                "low": round(price - 0.7, 6),
                "close": round(price, 6),
                "volume": 1_000_000 + (index % 17) * 25_000,
            }
        )
    return candles


class StubProvider:
    name = "stub"

    def __init__(self, *, failing: bool = False) -> None:
        self._candles = _zigzag_candles()
        self.failing = failing

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        if self.failing:
            raise MarketDataUnavailableError(f"no candles for {ticker}")
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 25, 8, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(str(self._candles[-1]["timestamp"])),
            fingerprint="a" * 64,
            candles=tuple(self._candles),
        )


def _install_provider(provider: StubProvider) -> None:
    app.dependency_overrides[get_market_data_provider] = lambda: provider


def _register_and_login(client: TestClient, fake_email_service, *, email: str) -> dict[str, str]:
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "display_name": "Scanner Tester"},
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


def _add_snapshot(
    db: Session,
    *,
    kind: str,
    symbol: str,
    score: float | None,
    rating: str | None,
    sector: str | None,
    as_of: datetime | None = None,
    payload_extra: dict | None = None,
) -> None:
    payload: dict = {"symbol": symbol, "sector": sector, "timeframe": "1D"}
    if payload_extra:
        payload.update(payload_extra)
    db.add(
        ScannerSnapshot(
            kind=kind,
            symbol=symbol,
            timeframe="1D",
            as_of=as_of or datetime.now(UTC),
            score=score,
            rating=rating,
            payload=payload,
        )
    )
    db.commit()


def test_scanner_routes_require_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/scanner/technical").status_code == 401
    assert client.get("/api/v1/scanner/technical/COMI").status_code == 401
    assert client.get("/api/v1/scanner/fibonacci").status_code == 401
    assert client.get("/api/v1/scanner/fibonacci/COMI").status_code == 401
    assert client.get("/api/v1/scanner/harmonic/COMI").status_code == 401
    assert client.get("/api/v1/scanner/smc/COMI").status_code == 401


def test_scanner_technical_returns_empty_list(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="empty-scan@example.com")

    response = client.get("/api/v1/scanner/technical", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body == {"items": [], "count": 0}


def test_scanner_technical_filters_sorts_and_limits(
    client: TestClient, fake_email_service, db_session: Session
) -> None:
    headers = _register_and_login(client, fake_email_service, email="filters-scan@example.com")
    base = datetime(2026, 7, 25, 10, tzinfo=UTC)
    _add_snapshot(
        db_session,
        kind="technical",
        symbol="COMI",
        score=92.5,
        rating="buy",
        sector="البنوك",
        as_of=base,
        payload_extra={"technicalScore": 92.5, "technicalRating": "buy"},
    )
    _add_snapshot(
        db_session,
        kind="technical",
        symbol="TMGH",
        score=65.0,
        rating="buy",
        sector="العقارات",
        as_of=base,
        payload_extra={"technicalScore": 65.0},
    )
    _add_snapshot(
        db_session,
        kind="technical",
        symbol="EAST",
        score=25.0,
        rating="sell",
        sector="الأغذية والمشروبات",
        as_of=base,
    )

    response = client.get("/api/v1/scanner/technical", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 3
    assert [item["symbol"] for item in body["items"]] == ["COMI", "TMGH", "EAST"]
    first = body["items"][0]
    assert first["kind"] == "technical"
    assert first["timeframe"] == "1D"
    assert first["score"] == 92.5
    assert first["rating"] == "buy"
    assert first["sector"] == "البنوك"
    assert first["technicalScore"] == 92.5
    assert datetime.fromisoformat(first["as_of"]) == base

    buys = client.get("/api/v1/scanner/technical", params={"rating": "buy"}, headers=headers)
    assert [item["symbol"] for item in buys.json()["items"]] == ["COMI", "TMGH"]

    banking = client.get("/api/v1/scanner/technical", params={"sector": "البنوك"}, headers=headers)
    assert [item["symbol"] for item in banking.json()["items"]] == ["COMI"]

    strong = client.get("/api/v1/scanner/technical", params={"min_score": 60}, headers=headers)
    assert [item["symbol"] for item in strong.json()["items"]] == ["COMI", "TMGH"]

    limited = client.get("/api/v1/scanner/technical", params={"limit": 1}, headers=headers)
    assert [item["symbol"] for item in limited.json()["items"]] == ["COMI"]


def test_scanner_limit_is_bounded(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="limit-scan@example.com")

    assert client.get("/api/v1/scanner/technical", params={"limit": 0}, headers=headers).status_code == 422
    assert client.get("/api/v1/scanner/technical", params={"limit": 1001}, headers=headers).status_code == 422


def test_scanner_fibonacci_returns_stored_snapshot(
    client: TestClient, fake_email_service, db_session: Session
) -> None:
    headers = _register_and_login(client, fake_email_service, email="fib-scan@example.com")
    _add_snapshot(
        db_session,
        kind="fibonacci",
        symbol="COMI",
        score=71.5,
        rating="buy",
        sector="البنوك",
        payload_extra={"levels": {"0.0": 100.0}, "currentZone": {"key": "0.236"}},
    )

    response = client.get("/api/v1/scanner/fibonacci/COMI", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "fibonacci"
    assert body["symbol"] == "COMI"
    assert body["score"] == 71.5
    assert body["rating"] == "buy"
    assert body["levels"]
    assert body["currentZone"]["key"] == "0.236"

    missing = client.get("/api/v1/scanner/fibonacci/TMGH", headers=headers)
    assert missing.status_code == 404
    assert missing.json()["detail"] == "No scanner snapshot for this symbol"


def test_scanner_harmonic_computes_on_demand(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="harm-live@example.com")
    _install_provider(StubProvider())

    response = client.get("/api/v1/scanner/harmonic/COMI", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "harmonic"
    assert body["symbol"] == "COMI"
    assert body["timeframe"] == "1D"
    assert body["engine_version"] == 2
    assert isinstance(body["patterns"], list)
    assert body["sector"] == "البنوك"
    assert body["rating"] in {"buy", "sell", "neutral"}


def test_scanner_harmonic_prefers_stored_snapshot(
    client: TestClient, fake_email_service, db_session: Session
) -> None:
    headers = _register_and_login(client, fake_email_service, email="harm-stored@example.com")
    _add_snapshot(
        db_session,
        kind="harmonic",
        symbol="COMI",
        score=58.0,
        rating="buy",
        sector="البنوك",
        payload_extra={"engine_version": 2, "patterns": [{"name": "Gartley", "score": 58.0}]},
    )
    _install_provider(StubProvider(failing=True))

    response = client.get("/api/v1/scanner/harmonic/COMI", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "COMI"
    assert body["patterns"][0]["name"] == "Gartley"


def test_scanner_harmonic_returns_404_without_candles(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="harm-empty@example.com")
    _install_provider(StubProvider(failing=True))

    response = client.get("/api/v1/scanner/harmonic/ZZZZ", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No scanner snapshot for this symbol"


def test_scanner_technical_computes_on_demand(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="tech-live@example.com")
    _install_provider(StubProvider())

    response = client.get("/api/v1/scanner/technical/COMI", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "technical"
    assert body["symbol"] == "COMI"
    assert body["timeframe"] == "1D"
    assert 0.0 <= float(body["technicalScore"]) <= 100.0
    assert body["technicalRating"] in {"buy", "sell", "neutral"}
    assert body["rating"] in {"buy", "sell", "neutral"}
    for key in (
        "rsi14",
        "macd",
        "macdSignal",
        "macdHistogram",
        "adx14",
        "atr14",
        "atrPercent",
        "bbPosition",
        "sma20",
        "sma50",
        "sma200",
        "relativeVolume20",
        "stochasticK",
        "stochasticD",
        "mfi14",
    ):
        assert body[key] is not None, key


def test_scanner_technical_prefers_stored_snapshot(
    client: TestClient, fake_email_service, db_session: Session
) -> None:
    headers = _register_and_login(client, fake_email_service, email="tech-stored@example.com")
    _add_snapshot(
        db_session,
        kind="technical",
        symbol="COMI",
        score=72.0,
        rating="buy",
        sector="البنوك",
        payload_extra={"technicalScore": 72.0, "technicalRating": "buy", "rsi14": 55.5},
    )
    _install_provider(StubProvider(failing=True))

    response = client.get("/api/v1/scanner/technical/COMI", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "COMI"
    assert body["technicalScore"] == 72.0
    assert body["rsi14"] == 55.5


def test_scanner_technical_returns_404_without_candles(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="tech-empty@example.com")
    _install_provider(StubProvider(failing=True))

    response = client.get("/api/v1/scanner/technical/ZZZZ", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No scanner snapshot for this symbol"


def test_scanner_smc_returns_engine_result(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="smc-live@example.com")
    _install_provider(StubProvider())

    response = client.get("/api/v1/scanner/smc/COMI", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "COMI"
    assert 0.0 <= body["score"] <= 100.0
    assert isinstance(body["details"], dict)
    assert body["details"]["zone"] in {"premium", "discount", "equilibrium"}
    assert isinstance(body["reasons"], list)


def test_scanner_smc_returns_404_for_unknown_ticker(client: TestClient, fake_email_service) -> None:
    headers = _register_and_login(client, fake_email_service, email="smc-empty@example.com")
    _install_provider(StubProvider(failing=True))

    response = client.get("/api/v1/scanner/smc/ZZZZ", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "No scanner snapshot for this symbol"
