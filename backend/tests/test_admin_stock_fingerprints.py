import pytest
from fastapi.testclient import TestClient

from app.main import app
from sahmi_kasban.fingerprint.models import (
    StockAlgorithmicSignature,
    TimeCyclePattern,
    AccumulationSweepPattern,
    AICriticEvaluation,
)
from sahmi_kasban.fingerprint.registry import StockSignatureRegistry


def test_fingerprint_registry_excel_and_endpoints(tmp_path, monkeypatch):
    registry = StockSignatureRegistry(tmp_path)
    sig = StockAlgorithmicSignature(
        ticker="COMI",
        updated_at="2026-09-14T00:00:00Z",
        time_cycle=TimeCyclePattern(dominant_cycle_sessions=35, stability_score=85.0),
        accumulation_sweep=AccumulationSweepPattern(avg_sweep_depth_pct=1.4, bounce_probability_pct=80.0),
        ai_critic=AICriticEvaluation(approved=True, confidence=90.0, summary="Excellent signature"),
        overall_quality_score=85.0,
    )
    registry.save_signature(sig)

    assert registry.get_signature("COMI") is not None

    excel_file = tmp_path / "test_export.xlsx"
    out_path = registry.export_to_excel(excel_file)
    assert out_path.exists()
