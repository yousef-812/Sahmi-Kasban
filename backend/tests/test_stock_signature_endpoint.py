from fastapi.testclient import TestClient

import sahmi_kasban.fingerprint as fingerprint
from app.main import app
from sahmi_kasban.fingerprint.models import (
    AICriticEvaluation,
    AccumulationSweepPattern,
    StockAlgorithmicSignature,
    TimeCyclePattern,
)


def test_public_stock_signature_uses_stability_score(tmp_path, monkeypatch) -> None:
    registry = fingerprint.StockSignatureRegistry(tmp_path)
    registry.save_signature(
        StockAlgorithmicSignature(
            ticker="COMI",
            updated_at="2026-09-14T00:00:00Z",
            time_cycle=TimeCyclePattern(dominant_cycle_sessions=35, stability_score=85.0),
            accumulation_sweep=AccumulationSweepPattern(
                avg_sweep_depth_pct=1.4, bounce_probability_pct=80.0
            ),
            ai_critic=AICriticEvaluation(
                approved=True, confidence=90.0, summary="Excellent signature"
            ),
            overall_quality_score=85.0,
        )
    )
    monkeypatch.setattr(fingerprint, "StockSignatureRegistry", lambda: registry)

    response = TestClient(app).get("/api/v1/stocks/COMI/signature")

    assert response.status_code == 200
    assert response.json()["cycle_stability_score"] == 85.0
