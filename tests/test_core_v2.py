from __future__ import annotations

import pandas as pd

from sahmi_kasban.backtesting import walk_forward_backtest
from sahmi_kasban.models import AnalysisReport, EngineResult
from sahmi_kasban.scoring import calculate_score_diagnostics


def engine_result(name: str, score: float, confidence: float = 90.0) -> EngineResult:
    return EngineResult(name=name, score=score, confidence=confidence)


def test_conflict_reduces_confidence_and_shrinks_score() -> None:
    diagnostics = calculate_score_diagnostics(
        {
            "stock_qualification": engine_result("stock_qualification", 100),
            "market_environment": engine_result("market_environment", 85),
            "technical": engine_result("technical", 90),
            "smc": engine_result("smc", 25),
            "multi_timeframe": engine_result("multi_timeframe", 80),
            "quantitative": engine_result("quantitative", 20),
            "risk": engine_result("risk", 75),
        }
    )

    assert diagnostics.conflict is True
    assert diagnostics.confidence < diagnostics.base_confidence
    assert abs(diagnostics.final_score - 50) < abs(diagnostics.raw_score - 50)
    assert set(diagnostics.bearish_engines) == {"quantitative", "smc"}


def test_consensus_keeps_high_quality_score_direction() -> None:
    diagnostics = calculate_score_diagnostics(
        {
            "stock_qualification": engine_result("stock_qualification", 100),
            "market_environment": engine_result("market_environment", 78),
            "technical": engine_result("technical", 82),
            "smc": engine_result("smc", 72),
            "multi_timeframe": engine_result("multi_timeframe", 76),
            "quantitative": engine_result("quantitative", 74),
            "risk": engine_result("risk", 80),
        }
    )

    assert diagnostics.conflict is False
    assert diagnostics.final_score >= 70
    assert diagnostics.confidence >= 75
    assert len(diagnostics.bullish_engines) == 5


class FakeAnalyzer:
    def __init__(self) -> None:
        self.history_lengths: list[int] = []

    def analyze(self, ticker: str, candles: pd.DataFrame) -> AnalysisReport:
        self.history_lengths.append(len(candles))
        return AnalysisReport(
            ticker=ticker,
            signal="BUY",
            final_score=75,
            confidence=80,
            qualified=True,
            engines={},
        )


def test_walk_forward_never_exposes_future_candles() -> None:
    rows = []
    for index in range(100):
        close = 10 + index * 0.1
        rows.append(
            {
                "timestamp": pd.Timestamp("2025-01-01", tz="UTC")
                + pd.Timedelta(days=index),
                "open": close - 0.05,
                "high": close + 0.1,
                "low": close - 0.1,
                "close": close,
                "volume": 1_000_000,
            }
        )

    analyzer = FakeAnalyzer()
    summary = walk_forward_backtest(
        "COMI",
        pd.DataFrame(rows),
        analyzer=analyzer,
        min_train_size=60,
        horizon_sessions=5,
        step_sessions=10,
        neutral_band_pct=0,
    )

    assert summary.observations == 4
    assert analyzer.history_lengths == [60, 70, 80, 90]
    assert summary.buy_hit_rate_pct == 100
    assert summary.directional_accuracy_pct == 100
