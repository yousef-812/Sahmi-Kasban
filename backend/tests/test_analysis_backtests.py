from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.market_data.types import CandleSeries, MarketDataUnavailableError
from app.models import (
    AnalysisBacktestObservation,
    AnalysisBacktestResult,
    AnalysisBacktestRun,
)
from app.services.analysis_backtests import execute_analysis_backtest


class FakeBacktestProvider:
    name = "fake-backtest"

    def __init__(self, *, failing_tickers: set[str] | None = None) -> None:
        self.calls = 0
        self.failing_tickers = failing_tickers or set()

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls += 1
        symbol = ticker.upper()
        if symbol in self.failing_tickers:
            raise MarketDataUnavailableError(f"No history for {symbol}")

        start = datetime(2024, 1, 1, tzinfo=UTC)
        candles: list[dict[str, object]] = []
        for index in range(260):
            close = 90 + index * 0.11 + ((index % 9) - 4) * 0.08
            candles.append(
                {
                    "timestamp": (start + timedelta(days=index)).isoformat(),
                    "open": round(close - 0.2, 6),
                    "high": round(close + 0.8, 6),
                    "low": round(close - 0.9, 6),
                    "close": round(close, 6),
                    "volume": 1_000_000 + index * 1_000,
                }
            )
        return CandleSeries(
            ticker=symbol,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 29, 12, tzinfo=UTC),
            data_as_of=datetime.fromisoformat(str(candles[-1]["timestamp"])),
            fingerprint=(symbol.lower() + "f" * 64)[:64],
            candles=tuple(candles),
        )


def test_backtest_run_persists_observations_and_is_idempotent(
    db_session: Session,
) -> None:
    provider = FakeBacktestProvider()
    first = asyncio.run(
        execute_analysis_backtest(
            db_session,
            actor_user_id=None,
            request_key="corev2-comi-history-001",
            tickers=["COMI"],
            provider=provider,
            period="5y",
            min_train_size=200,
            horizon_sessions=5,
            step_sessions=20,
        )
    )

    assert first.idempotent is False
    assert first.run.status == "complete"
    assert first.run.engine_version == "core-v2.5"
    assert first.run.completed_tickers == 1
    assert first.run.failed_tickers == 0
    assert len(first.results) == 1
    assert first.results[0].status == "complete"
    assert first.results[0].observations == 3

    observations = db_session.scalars(
        select(AnalysisBacktestObservation).where(
            AnalysisBacktestObservation.result_id == first.results[0].id
        )
    ).all()
    assert len(observations) == 3
    assert all(item.cutoff_index in {200, 220, 240} for item in observations)

    second = asyncio.run(
        execute_analysis_backtest(
            db_session,
            actor_user_id=None,
            request_key="corev2-comi-history-001",
            tickers=["COMI"],
            provider=provider,
            period="5y",
            min_train_size=200,
            horizon_sessions=5,
            step_sessions=20,
        )
    )
    assert second.idempotent is True
    assert second.run.id == first.run.id
    assert provider.calls == 2
    assert len(db_session.scalars(select(AnalysisBacktestRun)).all()) == 1
    assert len(db_session.scalars(select(AnalysisBacktestResult)).all()) == 1


def test_backtest_run_retains_failed_tickers_as_partial_results(
    db_session: Session,
) -> None:
    provider = FakeBacktestProvider(failing_tickers={"FAIL"})
    execution = asyncio.run(
        execute_analysis_backtest(
            db_session,
            actor_user_id=None,
            request_key="corev2-partial-history-001",
            tickers=["COMI", "FAIL"],
            provider=provider,
            min_train_size=200,
            horizon_sessions=5,
            step_sessions=20,
        )
    )

    assert execution.run.status == "partial"
    assert execution.run.completed_tickers == 1
    assert execution.run.failed_tickers == 1
    assert {item.status for item in execution.results} == {"complete", "failed"}
    failed = next(item for item in execution.results if item.status == "failed")
    assert failed.ticker == "FAIL"
    assert failed.error_code == "MarketDataUnavailableError"
    assert execution.run.details["failures"][0]["ticker"] == "FAIL"
