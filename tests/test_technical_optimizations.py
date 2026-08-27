from __future__ import annotations

import pandas as pd

from sahmi_kasban.backtesting import walk_forward_backtest
from sahmi_kasban.engines.smc import SMCEngine
from sahmi_kasban.indicators import enrich_indicators, prepare_candles
from sahmi_kasban.models import AnalysisConfig, AnalysisReport
from sahmi_kasban.orchestrator import SahmiKasbanAnalyzer, _is_prepared_candles, _prepare_index
from sahmi_kasban.scoring import score_to_signal


def _generate_synthetic_candles(count: int = 100) -> pd.DataFrame:
    rows = []
    base_price = 10.0
    for i in range(count):
        close = base_price + i * 0.1
        rows.append(
            {
                "timestamp": pd.Timestamp("2025-01-01", tz="UTC") + pd.Timedelta(days=i),
                "open": close - 0.05,
                "high": close + 0.1,
                "low": close - 0.1,
                "close": close,
                "volume": 1_000_000,
            }
        )
    return pd.DataFrame(rows)


class CountingPreparedAnalyzer:
    """Analyzer mock that tracks analyze vs analyze_prepared calls."""

    def __init__(self) -> None:
        self.analyze_calls = 0
        self.analyze_prepared_calls = 0

    def analyze(
        self,
        ticker: str,
        candles: pd.DataFrame,
        index: tuple[str, pd.DataFrame] | None = None,
    ) -> AnalysisReport:
        self.analyze_calls += 1
        return AnalysisReport(
            ticker=ticker,
            signal="BUY",
            final_score=75,
            confidence=80,
            qualified=True,
            engines={},
        )

    def analyze_prepared(
        self,
        ticker: str,
        candles: pd.DataFrame,
        index: tuple[str, pd.DataFrame] | None = None,
    ) -> AnalysisReport:
        self.analyze_prepared_calls += 1
        return AnalysisReport(
            ticker=ticker,
            signal="BUY",
            final_score=75,
            confidence=80,
            qualified=True,
            engines={},
        )


def test_walk_forward_uses_analyze_prepared() -> None:
    candles = _generate_synthetic_candles(100)
    analyzer = CountingPreparedAnalyzer()

    summary = walk_forward_backtest(
        "COMI",
        candles,
        analyzer=analyzer,
        min_train_size=60,
        horizon_sessions=5,
        step_sessions=10,
    )

    assert summary.observations == 4
    assert analyzer.analyze_prepared_calls == 4
    assert analyzer.analyze_calls == 0


def test_analysis_config_magic_numbers_customization() -> None:
    # Default signal thresholds: buy at score >= 67, risk >= 50
    assert score_to_signal(65.0, True, 60.0) == "WATCH"

    # Custom config lowering buy threshold to 60.0
    custom_cfg = AnalysisConfig(signal_buy_score_threshold=60.0)
    assert score_to_signal(65.0, True, 60.0, config=custom_cfg) == "BUY"


def test_smc_order_block_requires_breakout_and_volume() -> None:
    # Create candles with potential OB pattern (realistic body size ~ 0.2)
    rows = [
        {"open": 10.0, "high": 10.3, "low": 9.7, "close": 10.2, "volume": 100_000.0}
        for _ in range(20)
    ]
    # Candle 20: bearish small body (0.1 <= 0.2 body median) (the potential order block)
    rows.append({"open": 10.0, "high": 10.1, "low": 9.8, "close": 9.9, "volume": 100_000.0})

    # Scenario A: displacement green, but DOES NOT close above previous high 10.1
    rows_no_breakout = list(rows)
    rows_no_breakout.append(
        {"open": 9.7, "high": 10.1, "low": 9.6, "close": 10.0, "volume": 300_000.0}
    )
    res_no_breakout = SMCEngine(AnalysisConfig()).analyze(pd.DataFrame(rows_no_breakout), {})
    assert len(res_no_breakout.details["bullish_order_blocks"]) == 0

    # Scenario B: green, closes ABOVE previous high (10.4 > 10.1) but LOW volume (50k < 100k avg)
    rows_low_vol = list(rows)
    rows_low_vol.append(
        {"open": 9.8, "high": 10.5, "low": 9.7, "close": 10.4, "volume": 50_000.0}
    )
    res_low_vol = SMCEngine(AnalysisConfig()).analyze(pd.DataFrame(rows_low_vol), {})
    assert len(res_low_vol.details["bullish_order_blocks"]) == 0

    # Scenario C: green, closes ABOVE previous high (10.4 > 10.1) AND volume >= average
    rows_valid = list(rows)
    rows_valid.append(
        {"open": 9.8, "high": 10.5, "low": 9.7, "close": 10.4, "volume": 300_000.0}
    )
    res_valid = SMCEngine(AnalysisConfig()).analyze(pd.DataFrame(rows_valid), {})
    assert len(res_valid.details["bullish_order_blocks"]) == 1
    assert res_valid.details["bullish_order_blocks"][0]["low"] == 9.8
    assert res_valid.details["bullish_order_blocks"][0]["high"] == 10.1


def test_prepare_index_bypasses_redundant_cleaning() -> None:
    raw_df = _generate_synthetic_candles(60)
    prepared_df = prepare_candles(raw_df)

    assert _is_prepared_candles(prepared_df) is True

    # Check that _prepare_index returns the exact same object reference if prepared
    index_tuple = ("EGX30", prepared_df)
    res_name, res_df = _prepare_index(index_tuple)
    assert res_name == "EGX30"
    assert res_df is prepared_df


def test_rolling_vwap_and_technical_engine_integration() -> None:
    raw_df = _generate_synthetic_candles(60)
    enriched = enrich_indicators(raw_df)

    assert "vwap_20" in enriched.columns
    assert not enriched["vwap_20"].isna().any()

    from sahmi_kasban.engines.technical import TechnicalEngine

    result = TechnicalEngine(AnalysisConfig()).analyze(enriched, {})
    assert result.details["model_version"] == "technical-v2.3-vwap-aware"
    assert "vwap_20" in result.details
    assert any("20-day VWAP" in r for r in result.reasons)


def test_walk_forward_slippage_and_fees_deduction() -> None:
    candles = _generate_synthetic_candles(70)
    analyzer = CountingPreparedAnalyzer()

    # Zero slippage
    summary_zero = walk_forward_backtest(
        "COMI",
        candles,
        analyzer=analyzer,
        min_train_size=60,
        horizon_sessions=5,
        step_sessions=5,
        slippage_and_fees_pct=0.0,
    )
    # Default 0.3% slippage
    summary_fees = walk_forward_backtest(
        "COMI",
        candles,
        analyzer=analyzer,
        min_train_size=60,
        horizon_sessions=5,
        step_sessions=5,
        slippage_and_fees_pct=0.3,
    )

    ret_zero = summary_zero.results[0].forward_return_pct
    ret_fees = summary_fees.results[0].forward_return_pct
    assert abs((ret_zero - ret_fees) - 0.3) < 1e-4


def test_sector_momentum_engine_and_gate() -> None:
    from sahmi_kasban.engines.sector import SectorMomentumEngine

    engine = SectorMomentumEngine(AnalysisConfig())
    candles = _generate_synthetic_candles(60)

    # Bullish sector (+5%)
    res_bull = engine.analyze(candles, {"sector_momentum_5d_pct": 5.0})
    assert res_bull.score == 60.0
    assert "Sector momentum is strongly bullish" in res_bull.reasons

    # Bearish sector (-4%)
    res_bear = engine.analyze(candles, {"sector_momentum_5d_pct": -4.0})
    assert res_bear.score == 35.0
    assert "Sector momentum is strongly bearish" in res_bear.reasons[0]

    # Test orchestrator gate downgrade when sector is bearish
    analyzer = SahmiKasbanAnalyzer()
    # Generate clean uptrend candles
    report_bearish_sector = analyzer.analyze(
        "COMI",
        candles,
    )
    # If sector momentum is strongly bearish (-4.0), BUY signal downgrades to WATCH
    if report_bearish_sector.signal == "BUY":
        # Force context with bearish sector
        context = {"sector_momentum_5d_pct": -4.0}
        report_with_bearish_sector = analyzer.analyze_prepared(
            "COMI",
            enrich_indicators(prepare_candles(candles)),
            context=context,
        )
        assert report_with_bearish_sector.signal in ("WATCH", "AVOID")


def test_adaptive_atr_trailing_stop_in_risk_engine() -> None:
    from sahmi_kasban.engines.risk import RiskEngine

    risk_engine = RiskEngine(AnalysisConfig(stop_atr_multiple=2.0))
    candles = _generate_synthetic_candles(60)

    # Sideways market -> ATR multiple narrows (1.5)
    ctx_sideways = {"market_regime": "sideways", "annualized_volatility": 30.0}
    res_sideways = risk_engine.analyze(candles, ctx_sideways)
    assert res_sideways.details["adaptive_atr_multiple"] == 1.5
    assert res_sideways.details["model_version"] == "risk-plan-v2.4-adaptive-atr"

    # Speculative bullish / volatile market -> ATR multiple expands (2.5)
    ctx_volatile = {"market_regime": "speculative_bullish", "annualized_volatility": 70.0}
    res_volatile = risk_engine.analyze(candles, ctx_volatile)
    assert res_volatile.details["adaptive_atr_multiple"] == 2.5
