from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace

from sqlalchemy.orm import Session

from app.api.routes.community_verification import _load_prediction_score
from app.market_data.types import CandleSeries, MarketDataUnavailableError
from app.services.daily_reports import _analyze_ticker
from app.services.prediction_evaluation import PredictionWindow


class RetryPredictionProvider:
    name = "retry-fake"

    def __init__(self) -> None:
        self.calls = 0

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls += 1
        if self.calls == 1:
            raise MarketDataUnavailableError("temporary provider delay")
        assert period == "6mo"
        assert interval == "1d"
        candle = {
            "timestamp": "2026-07-29T00:00:00+00:00",
            "open": 100.0,
            "high": 108.0,
            "low": 99.0,
            "close": 106.0,
            "volume": 1_000_000,
        }
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=datetime(2026, 7, 29, 15, tzinfo=UTC),
            data_as_of=datetime(2026, 7, 29, tzinfo=UTC),
            fingerprint="prediction-retry",
            candles=(candle,),
        )


class ShortHistoryProvider:
    name = "short-history"

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        source = datetime(2026, 7, 29, 12, tzinfo=UTC)
        candles = []
        for index in range(180):
            close = 20 + index * 0.01
            candles.append(
                {
                    "timestamp": (source - timedelta(days=179 - index)).isoformat(),
                    "open": close - 0.1,
                    "high": close + 0.2,
                    "low": close - 0.2,
                    "close": close,
                    "volume": 2_000_000,
                }
            )
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=source,
            data_as_of=source,
            fingerprint="short-history",
            candles=tuple(candles),
        )


def test_prediction_evidence_retries_then_uses_short_valid_history() -> None:
    provider = RetryPredictionProvider()
    window = PredictionWindow(
        session_dates=(date(2026, 7, 29),),
        eligible_at=datetime(2026, 7, 29, 15, tzinfo=UTC),
    )
    discussion = SimpleNamespace(
        ticker="COMI",
        frozen_prediction={
            "direction": "up",
            "target_price": 108.0,
            "deadline": "نهاية الجلسة",
            "claims": ["الوصول إلى 108"],
            "specificity": 0.9,
        },
    )

    score = asyncio.run(
        _load_prediction_score(
            market_provider=provider,
            discussion=discussion,
            window=window,
        )
    )

    assert provider.calls == 2
    assert score.market_outcome["session_count"] == 1
    assert score.market_outcome["actual_direction"] == "up"


def test_daily_scan_treats_short_history_as_exclusion_not_provider_failure() -> None:
    outcome = asyncio.run(
        _analyze_ticker(
            "COMI",
            db=Session(),  # type: ignore[arg-type]
            source_session_date=date(2026, 7, 29),
            provider=ShortHistoryProvider(),
            semaphore=asyncio.Semaphore(1),
        )
    )

    assert outcome.failure is None
    assert outcome.excluded_reason == "insufficient_history"
    assert outcome.candidate is None
