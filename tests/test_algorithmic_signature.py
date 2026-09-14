import pytest
import pandas as pd

from sahmi_kasban.orchestrator import SahmiKasbanAnalyzer
from sahmi_kasban.fingerprint.models import (
    StockAlgorithmicSignature,
    TimeCyclePattern,
    AccumulationSweepPattern,
    AICriticEvaluation,
)
from sahmi_kasban.fingerprint.registry import StockSignatureRegistry
from sahmi_kasban.fingerprint.extractor import FingerprintExtractor


def make_candles(count: int = 100) -> pd.DataFrame:
    data = []
    price = 50.0
    for i in range(count):
        price += (i % 5 - 2) * 0.5
        data.append(
            {
                "timestamp": pd.Timestamp("2025-01-01") + pd.Timedelta(days=i),
                "open": price - 0.1,
                "high": price + 0.5,
                "low": max(1.0, price - 0.5),
                "close": price,
                "volume": 500_000,
            }
        )
    return pd.DataFrame(data)


def test_fingerprint_extractor():
    candles = make_candles(120)
    extractor = FingerprintExtractor()
    tc = extractor.extract_time_cycle(candles)
    acc = extractor.extract_accumulation_sweep(candles)

    assert tc.dominant_cycle_sessions >= 10
    assert 0.0 <= tc.stability_score <= 100.0
    assert acc.avg_sweep_depth_pct >= 0.0
    assert 0.0 <= acc.bounce_probability_pct <= 100.0


def test_signature_registry(tmp_path):
    registry = StockSignatureRegistry(tmp_path)
    sig = StockAlgorithmicSignature(
        ticker="TEST",
        updated_at="2026-09-14T00:00:00Z",
        time_cycle=TimeCyclePattern(dominant_cycle_sessions=35, stability_score=80.0),
        accumulation_sweep=AccumulationSweepPattern(avg_sweep_depth_pct=1.5, bounce_probability_pct=85.0),
        ai_critic=AICriticEvaluation(approved=True, confidence=90.0),
        overall_quality_score=85.0,
    )

    registry.save_signature(sig)
    loaded = registry.get_signature("TEST")

    assert loaded is not None
    assert loaded.ticker == "TEST"
    assert loaded.time_cycle.dominant_cycle_sessions == 35

    excel_path = tmp_path / "signatures.xlsx"
    exported = registry.export_to_excel(excel_path)
    assert exported.exists()


def test_analyzer_with_signature(tmp_path):
    registry = StockSignatureRegistry(tmp_path)
    sig = StockAlgorithmicSignature(
        ticker="COMI",
        updated_at="2026-09-14T00:00:00Z",
        time_cycle=TimeCyclePattern(dominant_cycle_sessions=30, stability_score=80.0, next_window_in_sessions=2),
        accumulation_sweep=AccumulationSweepPattern(avg_sweep_depth_pct=1.2, bounce_probability_pct=80.0),
        ai_critic=AICriticEvaluation(approved=True, confidence=85.0),
        overall_quality_score=82.0,
    )
    registry.save_signature(sig)

    analyzer = SahmiKasbanAnalyzer()
    candles = make_candles(80)

    report = analyzer.analyze("COMI", candles, context={"stock_signature": sig})

    assert "algorithmic_signature" in report.engines
    algo_engine = report.engines["algorithmic_signature"]
    assert algo_engine.score > 0
    assert algo_engine.details["approved_by_critic"] is True
