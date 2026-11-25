from __future__ import annotations

import pandas as pd
import pytest

from sahmi_kasban.scanner import detect_pivots, latest_impulse, scan_fibonacci


def _frame_from_closes(closes: list[float]) -> pd.DataFrame:
    count = len(closes)
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2024-01-01", periods=count, freq="D", tz="UTC"),
            "open": closes,
            "high": [price + 0.5 for price in closes],
            "low": [price - 0.5 for price in closes],
            "close": closes,
            "volume": [1000.0] * count,
        }
    )


def _fib_frame() -> pd.DataFrame:
    closes: list[float] = []
    for index in range(6):
        closes.append(102.0 - index * (2.0 / 5.0))
    for index in range(1, 26):
        closes.append(100.0 + index * (50.0 / 25.0))
    for index in range(1, 16):
        closes.append(150.0 - index * (31.375 / 15.0))
    return _frame_from_closes(closes)


def _monotonic_frame(rows: int = 40) -> pd.DataFrame:
    return _frame_from_closes([100.0 + index for index in range(rows)])


def test_returns_none_for_short_history() -> None:
    assert scan_fibonacci(_frame_from_closes([100.0] * 10), symbol="SHORT") is None


def test_returns_none_when_no_pivots_form() -> None:
    assert scan_fibonacci(_monotonic_frame(), symbol="TREND") is None


def test_detect_pivots_and_latest_impulse() -> None:
    frame = _fib_frame()
    pivots = detect_pivots(frame)

    assert pivots, "expected pivots on the manufactured swing"
    kinds = [pivot["kind"] for pivot in pivots]
    assert all(kind in ("high", "low") for kind in kinds)
    assert all(left != right for left, right in zip(kinds, kinds[1:], strict=False))
    for pivot in pivots:
        assert set(pivot) == {"index", "timestamp", "price", "kind"}

    impulse = latest_impulse(pivots)
    assert impulse is not None
    start, end = impulse
    assert start["kind"] == "low"
    assert end["kind"] == "high"
    assert start["price"] < end["price"]


def test_detects_bullish_impulse_with_golden_zone() -> None:
    result = scan_fibonacci(_fib_frame(), symbol="GOLD", meta={"nameAr": "سهم", "sector": "banks"})

    assert result is not None
    assert result["symbol"] == "GOLD"
    assert result["nameAr"] == "سهم"
    assert result["sector"] == "banks"
    assert result["direction"] == "up"
    assert result["timeframe"] == "1D"
    assert result["anchorStart"]["kind"] == "low"
    assert result["anchorStart"]["price"] == pytest.approx(99.5)
    assert result["anchorEnd"]["kind"] == "high"
    assert result["anchorEnd"]["price"] == pytest.approx(150.5)
    assert result["anchorStart"]["date"] is not None
    assert result["swingPercent"] == pytest.approx(51.0 / 99.5 * 100.0)
    assert result["swingAtr"] > 0.0
    assert result["retracementPercent"] == pytest.approx((150.5 - 118.625) / 51.0 * 100.0)
    assert result["currentZone"]["key"] == "golden"
    assert result["currentZone"]["kind"] == "golden"
    assert result["currentZone"]["labelEn"] == "Golden Zone"
    assert result["currentZone"]["priceLow"] == pytest.approx(150.5 - 0.65 * 51.0)
    assert result["currentZone"]["priceHigh"] == pytest.approx(150.5 - 0.618 * 51.0)
    assert result["status"] == "testing"
    assert 0.0 <= result["score"] <= 100.0
    assert 0.0 <= result["confidence"] <= 100.0
    assert result["trendAligned"] in (0, 1)


def test_levels_use_contract_ratios_and_prices() -> None:
    result = scan_fibonacci(_fib_frame(), symbol="GOLD")

    assert result is not None
    levels = result["levels"]
    assert [level["ratio"] for level in levels] == [0.236, 0.382, 0.5, 0.618, 0.786]
    assert [level["key"] for level in levels] == ["23.6", "38.2", "50", "61.8", "78.6"]
    by_key = {level["key"]: level for level in levels}
    assert by_key["50"]["price"] == pytest.approx(125.0)
    assert by_key["61.8"]["price"] == pytest.approx(150.5 - 0.618 * 51.0)
    for level in levels:
        assert set(level) == {"key", "kind", "ratio", "price", "labelAr", "labelEn"}
        assert level["kind"] in ("support", "resistance")


def test_metrics_block_matches_contract() -> None:
    result = scan_fibonacci(_fib_frame(), symbol="GOLD")

    assert result is not None
    assert set(result["metrics"]) == {"atr14", "ema20", "ema50", "rsi14", "relativeVolume20", "turnover"}
    assert result["metrics"]["atr14"] > 0.0
    assert result["metrics"]["turnover"] == pytest.approx(result["price"] * 1000.0)


def test_scan_result_contains_all_contract_keys() -> None:
    result = scan_fibonacci(_fib_frame(), symbol="GOLD")

    assert result is not None
    expected = {
        "symbol",
        "nameAr",
        "sector",
        "price",
        "direction",
        "timeframe",
        "anchorStart",
        "anchorEnd",
        "swingPercent",
        "swingAtr",
        "retracementPercent",
        "currentZone",
        "distancePercent",
        "distanceAtr",
        "status",
        "score",
        "confidence",
        "trendAligned",
        "metrics",
        "levels",
    }
    assert set(result) == expected
    for anchor_key in ("anchorStart", "anchorEnd"):
        assert set(result[anchor_key]) == {"kind", "index", "price", "timestamp", "date"}
