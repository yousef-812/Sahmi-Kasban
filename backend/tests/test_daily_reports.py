from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.market_data.types import CandleSeries
from app.models import (
    MarketReport,
    MarketReportItem,
    MarketReportUnlock,
    MarketScanRun,
    User,
    WalletAccount,
    WalletEntry,
)
from app.services import daily_reports
from app.services.daily_reports import (
    DailyReportGenerationError,
    generate_daily_top10_report,
    unlock_market_report,
)
from app.services.wallet import InsufficientBalanceError


class FakeMarketDataProvider:
    name = "fake"

    def __init__(self, source_date: datetime) -> None:
        self.source_date = source_date
        self.calls: list[str] = []

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls.append(ticker)
        candles = []
        for index in range(200):
            close = 100.0 + index * 0.1
            candles.append(
                {
                    "timestamp": (
                        self.source_date - timedelta(days=199 - index)
                    ).isoformat(),
                    "open": close - 0.2,
                    "high": close + 0.5,
                    "low": close - 0.5,
                    "close": close,
                    "volume": 100_000 + index,
                }
            )
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=self.source_date,
            data_as_of=self.source_date,
            fingerprint=f"fingerprint-{ticker}",
            candles=tuple(candles),
        )


class FakeAnalyzer:
    def __init__(self, _config: object) -> None:
        pass

    def analyze(self, ticker: str, _frame: object) -> SimpleNamespace:
        score = 70 + int(ticker[-2:])
        return SimpleNamespace(
            to_dict=lambda: {
                "signal": "BUY" if score >= 75 else "WATCH",
                "final_score": min(score, 99),
                "confidence": min(score + 1, 99),
                "qualified": True,
                "entry": 118.0,
                "stop_loss": 112.0,
                "targets": [124.0, 130.0],
            }
        )


class FakeAIService:
    async def explain_stock_analysis(
        self,
        *,
        ticker: str,
        analysis_payload: dict,
        language: str,
    ) -> str:
        assert analysis_payload["signal"] in {"BUY", "WATCH"}
        assert language == "ar"
        return f"تفسير آلي للسهم {ticker}"


def _moment() -> datetime:
    return datetime(2026, 7, 26, 17, 5, tzinfo=ZoneInfo("Africa/Cairo"))


def _source_datetime() -> datetime:
    return datetime(2026, 7, 26, 12, 0, tzinfo=UTC)


def _tickers(count: int) -> tuple[str, ...]:
    return tuple(f"T{index:02d}" for index in range(count))


def _user_with_wallet(db: Session, *, balance_points: int) -> User:
    user = User(
        email=f"user-{balance_points}@example.com",
        password_hash="hashed-password",
        display_name="Test User",
        avatar_key="avatar_01",
        status="active",
        email_verified=True,
    )
    db.add(user)
    db.flush()
    db.add(WalletAccount(user_id=user.id, balance_points=balance_points))
    db.commit()
    return user


def test_daily_scan_creates_ranked_report_once(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(daily_reports, "SahmiKasbanAnalyzer", FakeAnalyzer)
    provider = FakeMarketDataProvider(_source_datetime())

    first = asyncio.run(
        generate_daily_top10_report(
            db_session,
            provider=provider,
            ai_service=FakeAIService(),
            moment=_moment(),
            tickers=_tickers(12),
        )
    )

    assert first.created is True
    assert first.report.target_session_date.isoformat() == "2026-07-27"
    assert first.scan_run.status == "complete"
    items = db_session.scalars(
        select(MarketReportItem)
        .where(MarketReportItem.report_id == first.report.id)
        .order_by(MarketReportItem.rank)
    ).all()
    assert len(items) == 10
    assert [item.rank for item in items] == list(range(1, 11))
    assert items[0].ticker == "T11"
    assert items[0].payload["explanation_source"] == "ai"
    assert len(provider.calls) == 12

    second = asyncio.run(
        generate_daily_top10_report(
            db_session,
            provider=provider,
            ai_service=FakeAIService(),
            moment=_moment(),
            tickers=_tickers(12),
        )
    )
    assert second.created is False
    assert second.report.id == first.report.id
    assert len(provider.calls) == 12
    assert db_session.scalar(select(func.count(MarketReport.id))) == 1
    assert db_session.scalar(select(func.count(MarketScanRun.id))) == 1


def test_daily_scan_failure_leaves_no_partial_report(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(daily_reports, "SahmiKasbanAnalyzer", FakeAnalyzer)
    provider = FakeMarketDataProvider(_source_datetime())

    with pytest.raises(DailyReportGenerationError):
        asyncio.run(
            generate_daily_top10_report(
                db_session,
                provider=provider,
                ai_service=FakeAIService(),
                moment=_moment(),
                tickers=_tickers(9),
            )
        )

    assert db_session.scalar(select(func.count(MarketReport.id))) == 0
    assert db_session.scalar(select(func.count(MarketReportItem.id))) == 0
    run = db_session.scalar(select(MarketScanRun))
    assert run is not None
    assert run.status == "failed"
    assert run.details["reason"] == "not_enough_eligible_candidates"


def test_report_unlock_charges_once(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(daily_reports, "SahmiKasbanAnalyzer", FakeAnalyzer)
    generated = asyncio.run(
        generate_daily_top10_report(
            db_session,
            provider=FakeMarketDataProvider(_source_datetime()),
            ai_service=FakeAIService(),
            moment=_moment(),
            tickers=_tickers(12),
        )
    )
    user = _user_with_wallet(db_session, balance_points=300)

    first = unlock_market_report(
        db_session,
        user=user,
        report_id=generated.report.id,
    )
    second = unlock_market_report(
        db_session,
        user=user,
        report_id=generated.report.id,
    )

    assert first.charged_points == 100
    assert first.balance_points == 200
    assert second.charged_points == 0
    assert second.balance_points == 200
    assert len(first.access.items) == 10
    assert db_session.scalar(select(func.count(MarketReportUnlock.id))) == 1
    assert (
        db_session.scalar(
            select(func.count(WalletEntry.id)).where(
                WalletEntry.entry_type == "market_report_debit"
            )
        )
        == 1
    )


def test_report_unlock_with_insufficient_balance_rolls_back(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(daily_reports, "SahmiKasbanAnalyzer", FakeAnalyzer)
    generated = asyncio.run(
        generate_daily_top10_report(
            db_session,
            provider=FakeMarketDataProvider(_source_datetime()),
            ai_service=FakeAIService(),
            moment=_moment(),
            tickers=_tickers(12),
        )
    )
    user = _user_with_wallet(db_session, balance_points=50)

    with pytest.raises(InsufficientBalanceError):
        unlock_market_report(
            db_session,
            user=user,
            report_id=generated.report.id,
        )

    account = db_session.scalar(
        select(WalletAccount).where(WalletAccount.user_id == user.id)
    )
    assert account is not None
    assert account.balance_points == 50
    assert db_session.scalar(select(func.count(MarketReportUnlock.id))) == 0
    assert db_session.scalar(select(func.count(WalletEntry.id))) == 0
