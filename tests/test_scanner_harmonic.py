from __future__ import annotations

import numpy as np
import pandas as pd

from sahmi_kasban.scanner import scan_harmonic


def _frame_from_closes(closes: list[float]) -> pd.DataFrame:
    count = len(closes)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=count, freq="D", tz="UTC"),
            "open": closes,
            "high": closes,
            "low": closes,
            "close": closes,
            "volume": [1000.0] * count,
        }
    )


def _segment(start_price: float, end_price: float, steps: int) -> list[float]:
    return [
        start_price + (end_price - start_price) * index / steps for index in range(1, steps + 1)
    ]


def _gartley_frame() -> pd.DataFrame:
    x_price, a_price = 100.0, 140.0
    b_price = a_price - 0.618 * (a_price - x_price)
    c_price = b_price + 0.70 * (a_price - b_price)
    d_price = a_price - 0.786 * (a_price - x_price)
    closes: list[float] = [108.0, 106.0, 104.0, 102.0, 101.0]
    closes.append(x_price)
    closes.extend(_segment(x_price, a_price, 8))
    closes.extend(_segment(a_price, b_price, 8))
    closes.extend(_segment(b_price, c_price, 8))
    closes.extend(_segment(c_price, d_price, 8))
    closes.extend([d_price + 0.2, d_price + 0.4, d_price + 0.6])
    return _frame_from_closes(closes)


def _random_frame(rows: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    returns = rng.normal(0.0, 1.0, rows) / 100.0
    closes = list(100.0 * np.exp(np.cumsum(returns)))
    return _frame_from_closes(closes)


def test_detects_textbook_bullish_gartley() -> None:
    result = scan_harmonic(_gartley_frame(), symbol="GART")

    assert result["symbol"] == "GART"
    assert result["engine_version"] == 2
    assert result["pivot_count"] == 5
    assert len(result["patterns"]) == 1

    pattern = result["patterns"][0]
    assert pattern["type"] == "gartley"
    assert pattern["status"] == "complete"
    assert pattern["score"] > 80.0
    assert set(pattern) == {"type", "points", "ratios", "status", "score"}
    assert set(pattern["points"]) == {"X", "A", "B", "C", "D"}

    points = pattern["points"]
    assert points["X"]["kind"] == "low"
    assert points["A"]["kind"] == "high"
    assert points["B"]["kind"] == "low"
    assert points["C"]["kind"] == "high"
    assert points["D"]["kind"] == "low"
    assert points["X"]["price"] == 100.0
    assert points["A"]["price"] == 140.0

    ratios = pattern["ratios"]
    assert abs(ratios["ab"] - 0.618) < 1e-6
    assert abs(ratios["xd"] - 0.786) < 1e-6
    assert 1.15 <= ratios["cd"] <= 1.65
    assert 0.30 <= ratios["bc"] <= 0.95


def test_pivot_levels_report_positions() -> None:
    result = scan_harmonic(_gartley_frame(), symbol="GART")

    levels = result["pivot_levels"]
    assert len(levels) == 5
    assert [level["kind"] for level in levels] == ["low", "high", "low", "high", "low"]
    for level in levels:
        assert set(level) == {"index", "price", "kind"}


def test_random_walk_produces_no_false_positives() -> None:
    result = scan_harmonic(_random_frame(), symbol="RANDOM")

    assert result["patterns"] == []
    assert result["engine_version"] == 2


def test_short_history_returns_empty_patterns() -> None:
    result = scan_harmonic(_frame_from_closes([100.0 + index for index in range(10)]), symbol="TINY")

    assert result["symbol"] == "TINY"
    assert result["patterns"] == []
    assert result["pivot_count"] == 0
    assert result["pivot_levels"] == []
    assert result["engine_version"] == 2
