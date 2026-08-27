from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.schemas.analysis_history import AnalysisHistoryItem, AnalysisHistoryResponse  # noqa: E402


def test_analysis_history_schemas() -> None:
    now = datetime.now(UTC)
    item = AnalysisHistoryItem(
        analysis_id="12345678-1234-5678-1234-567812345678",
        ticker="COMI",
        signal="BUY",
        score=88.5,
        confidence=0.92,
        price_at_analysis=76.5,
        data_as_of=now,
        engine_version="v2.4",
        cached=True,
    )
    assert item.ticker == "COMI"
    assert item.signal == "BUY"
    assert item.score == 88.5

    response = AnalysisHistoryResponse(items=[item], count=1)
    assert response.count == 1
    assert response.items[0].ticker == "COMI"
