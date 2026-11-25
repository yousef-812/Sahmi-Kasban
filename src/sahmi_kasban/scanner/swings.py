from __future__ import annotations

import pandas as pd


def detect_pivots(df: pd.DataFrame, *, left: int = 3, right: int = 3) -> list[dict]:
    """Detect swing highs/lows as strict local extrema over a ``left``/``right`` window."""
    for column in ("high", "low"):
        if column not in df.columns:
            raise ValueError(f"missing pivot column: {column}")

    highs = pd.to_numeric(df["high"], errors="coerce").to_numpy(dtype=float)
    lows = pd.to_numeric(df["low"], errors="coerce").to_numpy(dtype=float)
    count = len(highs)
    pivots: list[dict] = []
    if count == 0 or left < 1 or right < 1 or count - left - right < 1:
        return pivots

    timestamps = None
    if "timestamp" in df.columns:
        timestamps = pd.to_datetime(df["timestamp"], errors="coerce", utc=True).tolist()

    for index in range(left, count - right):
        high = highs[index]
        low = lows[index]
        neighbours = [j for j in range(index - left, index + right + 1) if j != index]
        is_high = pd.notna(high) and all(
            pd.notna(highs[j]) and high > highs[j] for j in neighbours
        )
        is_low = pd.notna(low) and all(pd.notna(lows[j]) and low < lows[j] for j in neighbours)
        if not (is_high or is_low):
            continue
        timestamp = None
        if timestamps is not None:
            raw = timestamps[index]
            if pd.notna(raw):
                timestamp = pd.Timestamp(raw).isoformat()
        if is_high:
            pivots.append({"index": index, "timestamp": timestamp, "price": float(high), "kind": "high"})
        if is_low:
            pivots.append({"index": index, "timestamp": timestamp, "price": float(low), "kind": "low"})
    return _alternate(pivots)


def _alternate(pivots: list[dict]) -> list[dict]:
    """Collapse consecutive pivots of the same kind, keeping the more extreme one."""
    alternating: list[dict] = []
    for pivot in pivots:
        if not alternating or alternating[-1]["kind"] != pivot["kind"]:
            alternating.append(pivot)
            continue
        previous = alternating[-1]
        if pivot["kind"] == "high" and pivot["price"] > previous["price"]:
            alternating[-1] = pivot
        elif pivot["kind"] == "low" and pivot["price"] < previous["price"]:
            alternating[-1] = pivot
    return alternating


def latest_impulse(pivots: list[dict]) -> tuple[dict, dict] | None:
    """Return the most recent (start, end) swing leg as a low→high or high→low pair."""
    alternating = _alternate(list(pivots))
    if len(alternating) < 2:
        return None
    start, end = alternating[-2], alternating[-1]
    if start["kind"] == end["kind"]:
        return None
    return start, end
