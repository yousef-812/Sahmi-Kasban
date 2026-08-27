from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.market_data.types import CandleSeries
from app.models import (
    MarketReport,
    MarketReportEvaluation,
    MarketReportItem,
    MarketReportItemOutcome,
)
from app.services.report_performance import (
    ReportEvaluationNotDueError,
    evaluate_due_market_reports,
    evaluate_market_report,
)


class FakePerformanceProvider:
    name = "fake-performance"

    def __init__(self, candles_by_ticker: dict[str, tuple[dict[str, object], ...]]) -> None:
        self.candles_by_ticker = candles_by_ticker
        self.calls: list[str] = []

    async def get_history(
        self,
        ticker: str,
        *,
        period: str,
        interval: str,
    ) -> CandleSeries:
        self.calls.append(ticker)
        candles = self.candles_by_ticker.get(ticker, ())
        data_as_of = datetime(2026, 7, 27, 14, 0, tzinfo=UTC)
        return CandleSeries(
            ticker=ticker,
            provider=self.name,
            interval=interval,
            period=period,
            fetched_at=data_as_of,
            data_as_of=data_as_of,
            fingerprint=f"performance-{ticker}-{len(candles)}",
            candles=candles,
        )


def _moment(day: int, hour: int = 17, minute: int = 5) -> datetime:
    return datetime(2026, 7, day, hour, minute, tzinfo=ZoneInfo("Africa/Cairo"))


def _candle(
    day: int,
    *,
    open_price: float,
    high: float,
    low: float,
    close: float,
) -> dict[str, object]:
    return {
        "timestamp": datetime(2026, 7, day, 12, 0, tzinfo=UTC).isoformat(),
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": 250_000,
    }


def _create_report(
    db: Session,
    *,
    target_session_date: date,
    items: tuple[dict[str, object], ...],
) -> MarketReport:
    report = MarketReport(
        target_session_date=target_session_date,
        status="complete",
        generated_at=datetime(2026, 7, 26, 15, 5, tzinfo=UTC),
        source_snapshot={"source_session_date": "2026-07-26"},
        market_summary={"title": "Daily Top 10"},
    )
    db.add(report)
    db.flush()
    for rank, item in enumerate(items, start=1):
        db.add(
            MarketReportItem(
                report_id=report.id,
                ticker=str(item["ticker"]),
                rank=rank,
                score_bp=8000 - rank,
                payload={
                    "ticker": item["ticker"],
                    "rank": rank,
                    "price_at_analysis": item["price_at_analysis"],
                    "expected_direction": item.get("expected_direction", "up"),
                    "analysis": {
                        "stop_loss": item.get("stop_loss"),
                        "targets": item.get("targets", []),
                    },
                },
            )
        )
    db.commit()
    return report


def test_report_evaluation_retains_negative_results_and_is_idempotent(
    db_session: Session,
) -> None:
    report = _create_report(
        db_session,
        target_session_date=date(2026, 7, 27),
        items=(
            {
                "ticker": "NEG",
                "price_at_analysis": 100,
                "stop_loss": 95,
                "targets": [105, 110],
            },
            {
                "ticker": "POS",
                "price_at_analysis": 50,
                "stop_loss": 47,
                "targets": [55, 60],
            },
        ),
    )
    provider = FakePerformanceProvider(
        {
            "NEG": (
                _candle(27, open_price=100, high=108, low=94, close=97),
            ),
            "POS": (
                _candle(27, open_price=51, high=60, low=49, close=55),
            ),
        }
    )

    first = asyncio.run(
        evaluate_market_report(
            db_session,
            report_id=report.id,
            provider=provider,
            moment=_moment(27),
        )
    )

    assert first.idempotent is False
    assert first.evaluation.status == "complete"
    assert first.evaluation.evaluated_count == 2
    assert len(first.outcomes) == 2
    negative = first.outcomes[0]
    assert negative.status == "complete"
    assert negative.return_bp == -300
    assert negative.max_upside_bp == 800
    assert negative.max_drawdown_bp == -600
    assert negative.direction_correct is True
    assert negative.target_one_hit is True
    assert negative.target_two_hit is False
    assert negative.stop_loss_hit is True
    assert negative.evidence["negative_results_retained"] is True

    second = asyncio.run(
        evaluate_market_report(
            db_session,
            report_id=report.id,
            provider=provider,
            moment=_moment(27, 18),
        )
    )

    assert second.idempotent is True
    assert len(provider.calls) == 2
    assert db_session.scalar(select(func.count(MarketReportEvaluation.id))) == 1
    assert db_session.scalar(select(func.count(MarketReportItemOutcome.id))) == 2


def test_report_evaluation_rejects_requests_before_target_close(
    db_session: Session,
) -> None:
    report = _create_report(
        db_session,
        target_session_date=date(2026, 7, 27),
        items=({"ticker": "EARLY", "price_at_analysis": 100},),
    )

    with pytest.raises(ReportEvaluationNotDueError):
        asyncio.run(
            evaluate_market_report(
                db_session,
                report_id=report.id,
                provider=FakePerformanceProvider({}),
                moment=_moment(27, 14, 59),
            )
        )

    assert db_session.scalar(select(func.count(MarketReportEvaluation.id))) == 0


def test_incomplete_market_data_retries_without_duplicate_outcome(
    db_session: Session,
) -> None:
    report = _create_report(
        db_session,
        target_session_date=date(2026, 7, 27),
        items=(
            {
                "ticker": "RETRY",
                "price_at_analysis": 20,
                "stop_loss": 18,
                "targets": [22, 24],
            },
        ),
    )
    provider = FakePerformanceProvider({"RETRY": ()})

    first = asyncio.run(
        evaluate_market_report(
            db_session,
            report_id=report.id,
            provider=provider,
            moment=_moment(27),
        )
    )
    assert first.evaluation.status == "partial"
    assert first.evaluation.pending_count == 1
    assert first.outcomes[0].status == "pending_data"
    assert first.outcomes[0].evidence["retryable"] is True

    provider.candles_by_ticker["RETRY"] = (
        _candle(27, open_price=20, high=23, low=19, close=22),
    )
    second = asyncio.run(
        evaluate_market_report(
            db_session,
            report_id=report.id,
            provider=provider,
            moment=_moment(28),
        )
    )

    assert second.evaluation.status == "complete"
    assert second.evaluation.attempt_count == 2
    assert second.outcomes[0].status == "complete"
    assert second.outcomes[0].return_bp == 1000
    assert db_session.scalar(select(func.count(MarketReportItemOutcome.id))) == 1


def test_due_report_backfill_skips_future_reports(
    db_session: Session,
) -> None:
    due_report = _create_report(
        db_session,
        target_session_date=date(2026, 7, 27),
        items=({"ticker": "DUE", "price_at_analysis": 10},),
    )
    _create_report(
        db_session,
        target_session_date=date(2026, 7, 29),
        items=({"ticker": "FUTURE", "price_at_analysis": 10},),
    )
    provider = FakePerformanceProvider(
        {
            "DUE": (
                _candle(27, open_price=10, high=11, low=9, close=10.5),
            )
        }
    )

    result = asyncio.run(
        evaluate_due_market_reports(
            db_session,
            provider=provider,
            moment=_moment(28),
            limit=10,
        )
    )

    assert result.scanned_reports == 1
    assert result.completed_reports == 1
    assert result.skipped_reports == 1
    evaluation = db_session.scalar(
        select(MarketReportEvaluation).where(
            MarketReportEvaluation.report_id == due_report.id
        )
    )
    assert evaluation is not None
    assert evaluation.status == "complete"
