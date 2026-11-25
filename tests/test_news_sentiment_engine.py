from __future__ import annotations

import pandas as pd

from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer
from sahmi_kasban.engines import NewsSentimentEngine
from sahmi_kasban.models import EngineResult
from sahmi_kasban.scoring import (
    DEFAULT_WEIGHTS,
    DIRECTIONAL_ENGINES,
    calculate_score_diagnostics,
)


def _candles(count: int = 120) -> pd.DataFrame:
    rows = []
    for index in range(count):
        close = 100.0 + index * 0.5
        rows.append(
            {
                "open": close - 0.5,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1_000_000.0,
            }
        )
    return pd.DataFrame(rows)


def _engine() -> NewsSentimentEngine:
    return NewsSentimentEngine(AnalysisConfig())


def test_missing_context_returns_neutral_low_confidence() -> None:
    result = _engine().analyze(_candles(), {})

    assert result.name == "news_sentiment"
    assert result.score == 50.0
    assert result.confidence < 50.0
    assert result.details["coverage"] == "insufficient"
    assert result.details["sample_size"] == 0
    assert result.details["sentiment"] == 0.0
    assert any("missing" in reason for reason in result.reasons)


def test_zero_sample_size_is_insufficient() -> None:
    result = _engine().analyze(_candles(), {"news_sentiment": 0.8, "news_sample_size": 0})

    assert result.score == 50.0
    assert result.confidence < 50.0
    assert result.details["coverage"] == "insufficient"
    assert result.details["sentiment"] == 0.8
    assert any("sample size is zero" in reason for reason in result.reasons)


def test_positive_sentiment_scores_above_neutral() -> None:
    result = _engine().analyze(_candles(), {"news_sentiment": 0.6, "news_sample_size": 25})

    assert result.score == 80.0
    assert result.details["coverage"] == "normal"
    assert result.confidence >= 80.0
    assert any("bullish" in reason for reason in result.reasons)


def test_negative_sentiment_scores_below_neutral() -> None:
    result = _engine().analyze(_candles(), {"news_sentiment": -0.6, "news_sample_size": 25})

    assert result.score == 20.0
    assert result.details["coverage"] == "normal"
    assert any("bearish" in reason for reason in result.reasons)


def test_out_of_range_sentiment_is_clamped() -> None:
    high = _engine().analyze(_candles(), {"news_sentiment": 3.5, "news_sample_size": 30})
    low = _engine().analyze(_candles(), {"news_sentiment": -9.0, "news_sample_size": 30})

    assert high.score == 100.0
    assert high.details["sentiment"] == 1.0
    assert low.score == 0.0
    assert low.details["sentiment"] == -1.0


def test_non_numeric_sentiment_is_neutral_and_does_not_raise() -> None:
    result = _engine().analyze(_candles(), {"news_sentiment": "positive", "news_sample_size": 40})

    assert result.score == 50.0
    assert result.details["coverage"] == "insufficient"
    assert result.details["sentiment"] == 0.0
    assert any("Non-numeric" in reason for reason in result.reasons)


def test_small_sample_size_reports_low_coverage() -> None:
    result = _engine().analyze(_candles(), {"news_sentiment": 0.0, "news_sample_size": 4})

    assert result.details["coverage"] == "low"
    assert result.score == 50.0
    assert result.confidence < 85.0


def test_weight_is_registered_as_directional() -> None:
    assert DEFAULT_WEIGHTS["news_sentiment"] == 0.05
    assert "news_sentiment" in DIRECTIONAL_ENGINES


def test_diagnostics_buckets_neutral_news_sentiment() -> None:
    engines = {
        name: EngineResult(name=name, score=75.0, confidence=90.0)
        for name in (
            "market_environment",
            "technical",
            "smc",
            "algorithmic_signature",
            "multi_timeframe",
            "quantitative",
            "sector_momentum",
        )
    }
    engines["news_sentiment"] = EngineResult(name="news_sentiment", score=50.0, confidence=20.0)

    diagnostics = calculate_score_diagnostics(engines)

    assert "news_sentiment" in diagnostics.neutral_engines
    assert "news_sentiment" not in diagnostics.bullish_engines
    assert "news_sentiment" not in diagnostics.bearish_engines
    assert diagnostics.conflict is False


def test_orchestrator_runs_news_sentiment_with_neutral_default() -> None:
    report = SahmiKasbanAnalyzer(AnalysisConfig()).analyze("COMI", _candles())

    result = report.engines["news_sentiment"]
    assert result.score == 50.0
    assert result.details["coverage"] == "insufficient"
    assert "news_sentiment" in report.analysis_quality["neutral_engines"]


def test_orchestrator_forwards_sentiment_context() -> None:
    report = SahmiKasbanAnalyzer(AnalysisConfig()).analyze(
        "COMI",
        _candles(),
        context={"news_sentiment": 0.9, "news_sample_size": 15},
    )

    assert report.engines["news_sentiment"].score == 95.0
    assert report.engines["news_sentiment"].details["coverage"] == "normal"
