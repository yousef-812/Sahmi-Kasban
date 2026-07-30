from __future__ import annotations

import pandas as pd
import pytest

from sahmi_kasban import SahmiKasbanAnalyzer
from sahmi_kasban.indicators import enrich_indicators, prepare_candles


def _candles() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for index in range(280):
        close = 40.0 + index * 0.08 + ((index % 11) - 5) * 0.04
        rows.append(
            {
                "timestamp": pd.Timestamp("2025-01-01", tz="UTC")
                + pd.Timedelta(days=index),
                "open": close - 0.1,
                "high": close + 0.35,
                "low": close - 0.3,
                "close": close,
                "volume": 900_000 + (index % 9) * 20_000,
            }
        )
    return pd.DataFrame(rows)


def test_prepared_prefix_matches_individually_enriched_analysis() -> None:
    raw = _candles()
    prepared = enrich_indicators(prepare_candles(raw))
    analyzer = SahmiKasbanAnalyzer()

    for cutoff in (200, 225, 260, 279):
        incremental = analyzer.analyze("COMI", raw.iloc[:cutoff])
        reused = analyzer.analyze_prepared("COMI", prepared.iloc[:cutoff])
        assert reused.to_dict() == incremental.to_dict()


def test_prepared_analysis_rejects_unenriched_frames() -> None:
    analyzer = SahmiKasbanAnalyzer()
    with pytest.raises(ValueError, match="missing indicator columns"):
        analyzer.analyze_prepared("COMI", _candles())
