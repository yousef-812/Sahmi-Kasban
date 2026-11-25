"""Volume profile (POC / value area) from OHLCV candles.

Each candle's volume is split equally across the price bins its ``[low, high]``
range touches, so the sum of bin volumes equals the sum of candle volumes
exactly. The point of control (POC) is the highest-volume bin; the value area
grows from the POC outward (larger adjacent bin first) until it covers the
requested share of total volume — the classic market-profile expansion.

This is a daily-candle approximation: real intraday volume-at-price needs
tick data, which EGX does not expose for free (same limit as market depth).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_VALUE_AREA_PCT = 0.70


def _value_area(
    bin_volumes: np.ndarray,
    value_area_pct: float,
) -> tuple[int, int]:
    """Return the [start, end] bin indices of the value area around the POC."""
    poc_index = int(np.argmax(bin_volumes))
    total = float(bin_volumes.sum())
    if total <= 0:
        return poc_index, poc_index

    target = total * value_area_pct
    covered = float(bin_volumes[poc_index])
    start = end = poc_index
    while covered < target and (start > 0 or end < len(bin_volumes) - 1):
        above = float(bin_volumes[end + 1]) if end + 1 < len(bin_volumes) else -1.0
        below = float(bin_volumes[start - 1]) if start > 0 else -1.0
        if above >= below:
            end += 1
            covered += above
        else:
            start -= 1
            covered += below
    return start, end


def build_volume_profile(
    df: pd.DataFrame,
    *,
    bins: int = 24,
    value_area_pct: float = DEFAULT_VALUE_AREA_PCT,
) -> dict[str, object] | None:
    """Build the volume profile of a prepared candle frame, or ``None`` if empty."""
    if df.empty:
        return None
    lows = df["low"].astype(float).to_numpy()
    highs = df["high"].astype(float).to_numpy()
    volumes = df["volume"].astype(float).to_numpy()

    total_volume = float(volumes.sum())
    if total_volume <= 0:
        return None

    price_low = float(lows.min())
    price_high = float(highs.max())
    bin_count = max(1, bins)
    if price_high <= price_low:
        edges = np.array([price_low, price_high if price_high > price_low else price_low + 1e-9])
        bin_count = 1
    else:
        edges = np.linspace(price_low, price_high, bin_count + 1)

    bin_volumes = np.zeros(len(edges) - 1, dtype=float)
    for low, high, volume in zip(lows, highs, volumes, strict=True):
        first = max(0, int(np.searchsorted(edges, low, side="right") - 1))
        last = min(len(bin_volumes) - 1, int(np.searchsorted(edges, high, side="left") - 1))
        if last < first:
            last = first
        touched = last - first + 1
        bin_volumes[first : last + 1] += volume / touched

    poc_index = int(np.argmax(bin_volumes))
    start, end = _value_area(bin_volumes, value_area_pct)
    value_volume = float(bin_volumes[start : end + 1].sum())
    above_volume = float(bin_volumes[end + 1 :].sum())
    below_volume = float(bin_volumes[:start].sum())

    return {
        "poc": round(float((edges[poc_index] + edges[poc_index + 1]) / 2), 4),
        "value_area_high": round(float(edges[end + 1]), 4),
        "value_area_low": round(float(edges[start]), 4),
        "bins": [
            {
                "price_low": round(float(edges[index]), 4),
                "price_high": round(float(edges[index + 1]), 4),
                "volume": round(float(bin_volumes[index]), 2),
            }
            for index in range(len(bin_volumes))
        ],
        "above_value_pct": round(above_volume / total_volume * 100.0, 2),
        "below_value_pct": round(below_volume / total_volume * 100.0, 2),
        "value_area_volume_pct": round(value_volume / total_volume * 100.0, 2),
    }
