"""Volume profile core — POC, value area conservation and edge cases."""

from __future__ import annotations

import pandas as pd
import pytest

from sahmi_kasban.indicators import prepare_candles
from sahmi_kasban.volume_profile import build_volume_profile


def _candles(rows: list[tuple[float, float, float, float, float]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows, columns=["open", "high", "low", "close", "volume"])
    frame["timestamp"] = pd.date_range("2026-01-01", periods=len(frame), tz="UTC")
    return prepare_candles(frame)


def _three_zone_frame() -> pd.DataFrame:
    rows: list[tuple[float, float, float, float, float]] = []
    # منطقة قليلة الحجم قرب 100-102
    for index in range(10):
        rows.append(
            (
                100.0 + index * 0.2,
                101.0 + index * 0.2,
                100.0 + index * 0.2,
                100.5 + index * 0.2,
                100.0,
            )
        )
    # منطقة كثيفة قرب 110-112 (POC)
    for index in range(20):
        rows.append(
            (
                110.0 + index * 0.1,
                111.0 + index * 0.1,
                110.0 + index * 0.1,
                110.5 + index * 0.1,
                1000.0,
            )
        )
    # منطقة متوسطة قرب 120-122
    for index in range(8):
        rows.append(
            (
                120.0 + index * 0.25,
                121.0 + index * 0.25,
                120.0 + index * 0.25,
                120.5 + index * 0.25,
                500.0,
            )
        )
    return _candles(rows)


def test_bin_volumes_sum_to_candle_volumes() -> None:
    profile = build_volume_profile(_three_zone_frame())

    assert profile is not None
    total = sum(bin_["volume"] for bin_ in profile["bins"])
    assert total == pytest.approx(10 * 100.0 + 20 * 1000.0 + 8 * 500.0, rel=1e-6)


def test_poc_sits_in_the_densest_zone() -> None:
    profile = build_volume_profile(_three_zone_frame())

    assert profile is not None
    poc = float(profile["poc"])
    assert 109.0 < poc < 113.0
    poc_bin = next(
        bin_ for bin_ in profile["bins"] if bin_["price_low"] <= poc <= bin_["price_high"]
    )
    largest = max(profile["bins"], key=lambda bin_: bin_["volume"])
    assert poc_bin is largest


def test_value_area_brackets_poc_and_covers_target() -> None:
    profile = build_volume_profile(_three_zone_frame())

    assert profile is not None
    assert profile["value_area_low"] <= profile["poc"] <= profile["value_area_high"]
    assert profile["value_area_volume_pct"] >= 70.0
    assert profile["above_value_pct"] + profile["below_value_pct"] + profile[
        "value_area_volume_pct"
    ] == pytest.approx(100.0, abs=0.5)


def test_flat_range_collapses_to_one_bin() -> None:
    profile = build_volume_profile(_candles([(50.0, 50.0, 50.0, 50.0, 1000.0)] * 5))

    assert profile is not None
    assert len(profile["bins"]) == 1
    assert profile["poc"] == pytest.approx(50.0, abs=1e-3)
    assert profile["value_area_low"] == pytest.approx(50.0, abs=1e-3)
    assert profile["above_value_pct"] == pytest.approx(0.0)


def test_empty_or_zero_volume_frames_return_none() -> None:
    assert build_volume_profile(pd.DataFrame()) is None
    assert build_volume_profile(_candles([(50.0, 51.0, 49.0, 50.0, 0.0)] * 3)) is None
