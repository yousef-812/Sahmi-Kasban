from __future__ import annotations

import pandas as pd

from sahmi_kasban import AnalysisConfig, SahmiKasbanAnalyzer
from sahmi_kasban.models import EngineResult
from sahmi_kasban.scoring import (
    DEFAULT_WEIGHTS,
    DIRECTIONAL_ENGINES,
    FUNDAMENTAL_WEIGHTS,
    calculate_score_diagnostics,
    score_weights,
)

_FUNDAMENTAL_CONTEXT: dict[str, object] = {
    "pe_ratio": 5.5,
    "pb_ratio": 1.2,
    "dividend_yield_pct": 9.0,
    "roe_pct": 24.0,
    "total_debt": 50_000_000,
    "market_cap": 2_000_000_000,
    "net_income": 900_000_000,
    "eps": 4.0,
}


def _candles(count: int = 260) -> pd.DataFrame:
    rows = []
    for index in range(count):
        close = 100.0 + index * 0.35 + ((index % 11) - 5) * 0.4
        rows.append(
            {
                "open": close - 0.4,
                "high": close + 0.9,
                "low": close - 1.1,
                "close": close,
                "volume": 1_200_000.0 + (index % 13) * 25_000.0,
            }
        )
    return pd.DataFrame(rows)


def _directional_results(score: float = 70.0) -> dict[str, EngineResult]:
    return {
        name: EngineResult(name=name, score=score, confidence=90.0)
        for name in DEFAULT_WEIGHTS
    }


def test_analysis_config_flag_defaults_to_off() -> None:
    assert AnalysisConfig().enable_fundamentals is False
    assert AnalysisConfig(enable_fundamentals=True).enable_fundamentals is True


def test_default_weights_and_directional_set_exclude_investment() -> None:
    assert "investment" not in DEFAULT_WEIGHTS
    assert "investment" not in DIRECTIONAL_ENGINES
    assert FUNDAMENTAL_WEIGHTS == {"investment": 0.10}


def test_score_weights_merge_fundamentals_only_when_enabled() -> None:
    off = score_weights()
    on = score_weights(enable_fundamentals=True)

    assert off == DEFAULT_WEIGHTS
    assert "investment" not in off
    assert on["investment"] == 0.10
    assert all(on[name] == weight for name, weight in DEFAULT_WEIGHTS.items())


def test_investment_weight_blends_score_without_casting_directional_votes() -> None:
    engines = _directional_results()
    engines["investment"] = EngineResult(name="investment", score=95.0, confidence=85.0)

    off = calculate_score_diagnostics(engines, score_weights())
    on = calculate_score_diagnostics(engines, score_weights(enable_fundamentals=True))

    assert on.final_score > off.final_score
    assert "investment" not in on.bullish_engines
    assert "investment" not in on.bearish_engines
    assert "investment" not in on.neutral_engines
    assert on.conflict is False


def test_flag_off_is_identical_to_explicit_false() -> None:
    default_report = SahmiKasbanAnalyzer(AnalysisConfig()).analyze("COMI", _candles())
    explicit_report = SahmiKasbanAnalyzer(
        AnalysisConfig(enable_fundamentals=False),
    ).analyze("COMI", _candles())

    assert default_report.to_dict() == explicit_report.to_dict()


def test_flag_off_excludes_investment_engine_from_report() -> None:
    report = SahmiKasbanAnalyzer(AnalysisConfig()).analyze("COMI", _candles())

    assert "investment" not in report.engines
    quality = report.analysis_quality
    assert "investment" not in quality["failed_engines"]
    for bucket in ("bullish_engines", "bearish_engines", "neutral_engines"):
        assert "investment" not in quality[bucket]


def test_flag_on_runs_investment_engine_with_fundamentals_context() -> None:
    report = SahmiKasbanAnalyzer(AnalysisConfig(enable_fundamentals=True)).analyze(
        "COMI",
        _candles(),
        context=dict(_FUNDAMENTAL_CONTEXT),
    )

    result = report.engines["investment"]
    assert result.name == "investment"
    assert result.status == "complete"
    assert result.score > 70.0
    assert result.details["ticker"] == "COMI"
    assert result.details["pe_ratio"] == 5.5
    assert result.details["investment_category"] in {"dividend", "growth", "value", "balanced"}

    quality = report.analysis_quality
    assert "investment" not in quality["failed_engines"]
    for bucket in ("bullish_engines", "bearish_engines", "neutral_engines"):
        assert "investment" not in quality[bucket]


def test_flag_on_without_fundamentals_context_still_completes() -> None:
    report = SahmiKasbanAnalyzer(AnalysisConfig(enable_fundamentals=True)).analyze(
        "COMI",
        _candles(),
    )

    result = report.engines["investment"]
    assert result.status == "complete"
    assert 45.0 <= result.score <= 65.0
    assert report.signal in {"BUY", "WATCH", "AVOID"}
