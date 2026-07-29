from __future__ import annotations

import csv
import io
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from app.services.historical_replay_exports import (
    build_historical_replay_csv,
    calculate_replay_export_metrics,
)


def _row(
    *,
    ticker: str,
    score_bp: int | None,
    return_bp: int | None,
    signal: str | None,
    qualified: bool | None,
    status: str = "evaluated",
):
    return SimpleNamespace(
        id=uuid4(),
        ticker=ticker,
        analysis_date=date(2026, 7, 1),
        status=status,
        engine_version="core-v2.1",
        provider="fake",
        data_fingerprint="f" * 64,
        data_as_of=None,
        candle_count=250,
        signal=signal,
        score_bp=score_bp,
        confidence_bp=7000 if score_bp is not None else None,
        qualified=qualified,
        engines={"technical": {"score": 70}},
        trade_plan=None,
        warnings=[],
        analysis_quality={},
        entry=None,
        evaluation_date=date(2026, 7, 8) if return_bp is not None else None,
        exit=None,
        forward_return_bp=return_bp,
        max_upside_bp=None,
        max_drawdown_bp=None,
        correct=None,
        error_code=None,
        error_message=None,
    )


def test_metrics_compare_direction_to_same_day_market_benchmark() -> None:
    buy = _row(ticker="BUY", score_bp=8000, return_bp=500, signal="BUY", qualified=True)
    avoid = _row(
        ticker="AVOID",
        score_bp=4000,
        return_bp=100,
        signal="AVOID",
        qualified=True,
    )
    watch = _row(
        ticker="WATCH",
        score_bp=6000,
        return_bp=300,
        signal="WATCH",
        qualified=True,
    )
    excluded = _row(
        ticker="EXCLUDED",
        score_bp=9000,
        return_bp=200,
        signal="AVOID",
        qualified=False,
    )

    metrics = calculate_replay_export_metrics(
        [buy, avoid, watch, excluded],
        neutral_band_bp=100,
    )

    assert metrics[buy.id].benchmark_return_bp == 275
    assert metrics[buy.id].excess_return_bp == 225
    assert metrics[buy.id].benchmark_correct is True
    assert metrics[avoid.id].excess_return_bp == -175
    assert metrics[avoid.id].benchmark_correct is True
    assert metrics[watch.id].excess_return_bp == 25
    assert metrics[watch.id].benchmark_correct is True
    assert metrics[excluded.id].evaluation_scope == "eligibility_exclusion"
    assert metrics[excluded.id].benchmark_correct is None
    assert metrics[excluded.id].score_percentile is None
    assert metrics[buy.id].score_percentile == 100.0
    assert metrics[avoid.id].score_percentile == 33.33


def test_csv_includes_benchmark_columns_and_failed_ticker_records() -> None:
    analyzed = _row(
        ticker="COMI",
        score_bp=7800,
        return_bp=350,
        signal="BUY",
        qualified=True,
    )
    failed_task = SimpleNamespace(
        ticker="MISSING",
        status="failed",
        provider="tradingview",
        data_fingerprint=None,
        candle_count=0,
        error_code="provider_unavailable",
        error_message="provider failed",
    )
    db = MagicMock()
    db.scalars.side_effect = [
        SimpleNamespace(all=lambda: [analyzed]),
        SimpleNamespace(all=lambda: [failed_task]),
    ]
    job = SimpleNamespace(
        id=uuid4(),
        engine_version="core-v2.1",
        neutral_band_bp=100,
    )

    payload = build_historical_replay_csv(db, job=job).decode("utf-8-sig")
    records = list(csv.DictReader(io.StringIO(payload)))

    assert records[0]["record_type"] == "analysis_row"
    assert records[0]["market_benchmark_return_pct"] == "3.5"
    assert records[0]["excess_return_pct"] == "0.0"
    assert records[0]["score_percentile"] == "100.0"
    assert records[1]["record_type"] == "ticker_failure"
    assert records[1]["ticker"] == "MISSING"
    assert records[1]["status"] == "ticker_failed"
    assert records[1]["error_code"] == "provider_unavailable"
