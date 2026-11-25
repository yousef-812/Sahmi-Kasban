from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Environment
from app.jobs import scanner_refresh as scanner_refresh_job
from app.market_data.types import CandleSeries, MarketDataUnavailableError
from app.models import ScannerSnapshot
from app.services import scanner as scanner_service
from app.services.scanner import (
    build_harmonic_item,
    build_smc_item,
    get_scanner_item,
    get_scanner_items,
    refresh_scanner_snapshot,
)

START = datetime(2025, 9, 1, tzinfo=UTC)


def _zigzag_prices(count: int = 220) -> list[float]:
    prices: list[float] = []
    price = 100.0
    for index in range(count):
        price += 1.0 if index % 40 < 20 else -0.8
        prices.append(price)
    return prices


def _up_price(index: int) -> float:
    return 100.0 + index * 0.8


def _down_price(index: int) -> float:
    return 300.0 - index * 0.8


def _candles(close_of) -> list[dict[str, object]]:
    candles: list[dict[str, object]] = []
    for index in range(220):
        close = float(close_of(index))
        candles.append(
            {
                "timestamp": (START + timedelta(days=index)).isoformat(),
                "open": round(close - 0.2, 6),
                "high": round(close + 0.7, 6),
                "low": round(close - 0.7, 6),
                "close": round(close, 6),
                "volume": 1_000_000 + (index % 17) * 25_000,
            }
        )
    return candles


class StubProvider:
    """Market-data provider stub; no network is ever touched in tests."""

    name = "stub"

    def __init__(self, candles: list[dict[str, object]], *, failing: set[str] | None = None) -> None:
        self._candles = candles
        self.failing = failing or set()
        self.calls: list[str] = []

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls.append(ticker)
        if ticker in self.failing:
            raise MarketDataUnavailableError(f"no candles for {ticker}")
        last_timestamp = str(self._candles[-1]["timestamp"])
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 25, 8, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(last_timestamp),
            fingerprint="f" * 64,
            candles=tuple(self._candles),
        )


def _add_snapshot(
    db: Session,
    *,
    symbol: str,
    score: float | None,
    rating: str | None,
    sector: str | None,
    kind: str = "technical",
    as_of: datetime | None = None,
) -> None:
    db.add(
        ScannerSnapshot(
            kind=kind,
            symbol=symbol,
            timeframe="1D",
            as_of=as_of or datetime.now(UTC),
            score=score,
            rating=rating,
            payload={"symbol": symbol, "sector": sector, "technicalScore": score},
        )
    )
    db.commit()


def test_refresh_scanner_snapshot_stores_one_row_per_symbol(db_session: Session) -> None:
    provider = StubProvider(_candles(_up_price))

    result = asyncio.run(
        refresh_scanner_snapshot(db_session, provider, kind="technical", tickers=["COMI", "CBKD"])
    )

    assert result["kind"] == "technical"
    assert result["count"] == 2
    assert datetime.fromisoformat(str(result["as_of"])).tzinfo is not None

    rows = db_session.scalars(select(ScannerSnapshot)).all()
    assert {row.symbol for row in rows} == {"COMI", "CBKD"}
    technical = next(row for row in rows if row.symbol == "COMI")
    assert technical.kind == "technical"
    assert technical.timeframe == "1D"
    assert technical.rating == "buy"
    assert technical.payload["technicalRating"] == "buy"
    assert -100.0 <= float(technical.score) <= 100.0
    assert technical.payload["sector"] == "البنوك"
    assert "rsi14" in technical.payload


def test_refresh_scanner_snapshot_survives_symbol_failure(db_session: Session) -> None:
    provider = StubProvider(_candles(_up_price), failing={"CBKD"})

    result = asyncio.run(
        refresh_scanner_snapshot(
            db_session,
            provider,
            kind="technical",
            tickers=["COMI", "CBKD", "EAST"],
        )
    )

    assert result["count"] == 2
    symbols = {row.symbol for row in db_session.scalars(select(ScannerSnapshot)).all()}
    assert symbols == {"COMI", "EAST"}


def test_refresh_scanner_snapshot_rejects_unsupported_kind(db_session: Session) -> None:
    provider = StubProvider(_candles(_up_price))

    with pytest.raises(ValueError, match="Unsupported scanner kind"):
        asyncio.run(
            refresh_scanner_snapshot(db_session, provider, kind="momentum", tickers=["COMI"])
        )


def test_refresh_scanner_snapshot_replaces_previous_rows(db_session: Session) -> None:
    provider = StubProvider(_candles(_up_price))

    first = asyncio.run(
        refresh_scanner_snapshot(db_session, provider, kind="technical", tickers=["COMI", "CBKD"])
    )
    second = asyncio.run(
        refresh_scanner_snapshot(db_session, provider, kind="technical", tickers=["COMI", "CBKD"])
    )

    assert first["count"] == 2
    assert second["count"] == 2
    rows = db_session.scalars(select(ScannerSnapshot)).all()
    assert len(rows) == 2
    assert {row.symbol for row in rows} == {"COMI", "CBKD"}


def test_refresh_scanner_snapshot_downtrend_scores_as_sell(db_session: Session) -> None:
    provider = StubProvider(_candles(_down_price))

    asyncio.run(
        refresh_scanner_snapshot(db_session, provider, kind="technical", tickers=["COMI"])
    )

    row = db_session.scalar(select(ScannerSnapshot))
    assert row is not None
    assert row.rating == "sell"
    assert row.payload["technicalRating"] == "sell"
    assert float(row.score) <= -40.0


def test_refresh_scanner_snapshot_fibonacci_kind(db_session: Session) -> None:
    prices = _zigzag_prices()
    provider = StubProvider(_candles(lambda index: prices[index]))

    result = asyncio.run(
        refresh_scanner_snapshot(db_session, provider, kind="fibonacci", tickers=["COMI"])
    )

    assert result["kind"] == "fibonacci"
    assert result["count"] == 1

    row = db_session.scalar(select(ScannerSnapshot))
    assert row is not None
    assert row.kind == "fibonacci"
    assert row.payload["symbol"] == "COMI"
    assert row.payload["timeframe"] == "1D"
    assert row.payload["levels"]
    assert row.payload["currentZone"]["key"]
    assert row.payload["sector"] == "البنوك"
    assert row.rating in {"buy", "sell", "neutral"}
    assert 0.0 <= float(row.score) <= 100.0
    assert row.rating == scanner_service._score_rating(float(row.score))


def test_refresh_scanner_snapshot_harmonic_kind(db_session: Session) -> None:
    prices = _zigzag_prices()
    provider = StubProvider(_candles(lambda index: prices[index]))

    result = asyncio.run(
        refresh_scanner_snapshot(db_session, provider, kind="harmonic", tickers=["COMI"])
    )

    assert result["count"] == 1

    row = db_session.scalar(select(ScannerSnapshot))
    assert row is not None
    assert row.kind == "harmonic"
    assert row.payload["engine_version"] == 2
    assert isinstance(row.payload["patterns"], list)
    assert row.payload["timeframe"] == "1D"
    assert row.rating in {"buy", "sell", "neutral"}


def test_get_scanner_items_filters_sorts_and_limits(db_session: Session) -> None:
    base = datetime(2026, 7, 25, 10, tzinfo=UTC)
    _add_snapshot(db_session, symbol="COMI", score=90.0, rating="buy", sector="البنوك", as_of=base)
    _add_snapshot(
        db_session, symbol="TMGH", score=70.0, rating="buy", sector="العقارات", as_of=base
    )
    _add_snapshot(
        db_session,
        symbol="EAST",
        score=30.0,
        rating="sell",
        sector="الأغذية والمشروبات",
        as_of=base,
    )
    _add_snapshot(
        db_session,
        symbol="HRHO",
        score=None,
        rating=None,
        sector="الخدمات المالية",
        as_of=base,
    )

    items = asyncio.run(get_scanner_items(db_session, kind="technical"))
    assert [item["symbol"] for item in items] == ["COMI", "TMGH", "EAST", "HRHO"]
    assert items[0]["score"] == 90.0
    assert items[3]["score"] is None
    assert items[3]["as_of"] == base.isoformat()

    buys = asyncio.run(get_scanner_items(db_session, kind="technical", rating="buy"))
    assert [item["symbol"] for item in buys] == ["COMI", "TMGH"]

    banking = asyncio.run(get_scanner_items(db_session, kind="technical", sector="البنوك"))
    assert [item["symbol"] for item in banking] == ["COMI"]

    strong = asyncio.run(get_scanner_items(db_session, kind="technical", min_score=50.0))
    assert [item["symbol"] for item in strong] == ["COMI", "TMGH"]

    limited = asyncio.run(get_scanner_items(db_session, kind="technical", limit=2))
    assert [item["symbol"] for item in limited] == ["COMI", "TMGH"]

    stored = asyncio.run(get_scanner_items(db_session, kind="fibonacci"))
    assert stored == []


def test_get_scanner_items_returns_newest_snapshot_per_symbol(db_session: Session) -> None:
    old = datetime(2026, 7, 24, 10, tzinfo=UTC)
    new = datetime(2026, 7, 25, 10, tzinfo=UTC)
    _add_snapshot(db_session, symbol="COMI", score=40.0, rating="neutral", sector=None, as_of=old)
    _add_snapshot(db_session, symbol="COMI", score=88.0, rating="buy", sector=None, as_of=new)

    items = asyncio.run(get_scanner_items(db_session, kind="technical"))

    assert len(items) == 1
    assert items[0]["score"] == 88.0
    assert items[0]["as_of"] == new.isoformat()


def test_get_scanner_items_rejects_unsupported_kind(db_session: Session) -> None:
    with pytest.raises(ValueError, match="Unsupported scanner kind"):
        asyncio.run(get_scanner_items(db_session, kind="momentum"))


def test_get_scanner_item_looks_up_symbol(db_session: Session) -> None:
    _add_snapshot(db_session, symbol="COMI", score=61.0, rating="buy", sector="البنوك")

    item = asyncio.run(get_scanner_item(db_session, kind="technical", symbol="comi"))
    assert item is not None
    assert item["symbol"] == "COMI"
    assert item["score"] == 61.0
    assert item["rating"] == "buy"
    assert item["sector"] == "البنوك"
    assert item["timeframe"] == "1D"

    assert asyncio.run(get_scanner_item(db_session, kind="technical", symbol="ZZZZ")) is None
    assert asyncio.run(get_scanner_item(db_session, kind="technical", symbol="bad ticker!")) is None

    with pytest.raises(ValueError, match="Unsupported scanner kind"):
        asyncio.run(get_scanner_item(db_session, kind="momentum", symbol="COMI"))


def test_build_smc_item_returns_engine_result(db_session: Session) -> None:
    prices = _zigzag_prices()
    provider = StubProvider(_candles(lambda index: prices[index]))

    item = asyncio.run(build_smc_item(db_session, provider, "COMI"))

    assert item is not None
    assert item["symbol"] == "COMI"
    assert 0.0 <= item["score"] <= 100.0
    assert isinstance(item["details"], dict)
    assert item["details"]["zone"]
    assert isinstance(item["reasons"], list)


def test_build_smc_item_returns_none_without_candles(db_session: Session) -> None:
    provider = StubProvider(_candles(_up_price), failing={"ZZZZ"})

    assert asyncio.run(build_smc_item(db_session, provider, "not a ticker!")) is None
    assert asyncio.run(build_smc_item(db_session, provider, "ZZZZ")) is None


def test_build_harmonic_item_returns_pattern_payload(db_session: Session) -> None:
    prices = _zigzag_prices()
    provider = StubProvider(_candles(lambda index: prices[index]))

    item = asyncio.run(build_harmonic_item(db_session, provider, "COMI"))

    assert item is not None
    assert item["kind"] == "harmonic"
    assert item["symbol"] == "COMI"
    assert item["engine_version"] == 2
    assert isinstance(item["patterns"], list)
    assert item["sector"] == "البنوك"
    assert item["timeframe"] == "1D"


def test_build_harmonic_item_returns_none_for_invalid_symbol(db_session: Session) -> None:
    provider = StubProvider(_candles(_up_price))

    assert asyncio.run(build_harmonic_item(db_session, provider, "not a ticker!")) is None


def test_job_skips_in_test_environment() -> None:
    result = asyncio.run(scanner_refresh_job.run_scanner_refresh())

    assert result["status"] == "skipped"
    assert result["reason"] == "test_environment"


def test_job_skips_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = SimpleNamespace(
        app_env=Environment.DEVELOPMENT,
        scanner_refresh_enabled=False,
        scanner_refresh_minutes=15,
    )
    monkeypatch.setattr(scanner_refresh_job, "get_settings", lambda: settings)

    result = asyncio.run(scanner_refresh_job.run_scanner_refresh())

    assert result["status"] == "skipped"
    assert result["reason"] == "disabled"


def test_job_refreshes_technical_and_fibonacci(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    prices = _zigzag_prices()
    provider = StubProvider(_candles(lambda index: prices[index]))
    session_factory = sessionmaker(
        bind=db_session.get_bind(), autoflush=False, expire_on_commit=False
    )
    settings = SimpleNamespace(
        app_env=Environment.DEVELOPMENT,
        scanner_refresh_enabled=True,
        scanner_refresh_minutes=15,
    )

    async def _fake_tickers(db: Session) -> list[str]:
        return ["COMI", "CBKD"]

    monkeypatch.setattr(scanner_refresh_job, "get_settings", lambda: settings)
    monkeypatch.setattr(scanner_refresh_job, "SessionLocal", session_factory)
    monkeypatch.setattr(scanner_refresh_job, "get_market_data_provider", lambda: provider)
    monkeypatch.setattr(scanner_refresh_job, "_trading_session_now", lambda: True)
    monkeypatch.setattr(scanner_service, "resolve_scanner_tickers", _fake_tickers)

    db_session.commit()
    result = asyncio.run(scanner_refresh_job.run_scanner_refresh())

    assert result["status"] == "completed"
    assert result["count"] == 4
    assert set(result["kinds"]) == {"technical", "fibonacci"}
    assert result["failed_kinds"] == []

    db_session.expire_all()
    rows = db_session.scalars(select(ScannerSnapshot)).all()
    assert {(row.kind, row.symbol) for row in rows} == {
        ("technical", "COMI"),
        ("technical", "CBKD"),
        ("fibonacci", "COMI"),
        ("fibonacci", "CBKD"),
    }
