from __future__ import annotations

import pandas as pd

from sahmi_kasban.indicators import prepare_candles
from sahmi_kasban.scanner.swings import detect_pivots

ENGINE_VERSION = 2

MIN_CANDLES = 15

PATTERN_SPECS: dict[str, dict[str, tuple[float, float]]] = {
    "gartley": {"ab": (0.55, 0.68), "xd": (0.72, 0.85), "cd": (1.15, 1.65)},
    "bat": {"ab": (0.32, 0.55), "xd": (0.82, 0.95), "cd": (1.55, 2.70)},
    "butterfly": {"ab": (0.72, 0.85), "xd": (1.20, 1.35), "cd": (1.55, 2.30)},
    "crab": {"ab": (0.35, 0.65), "xd": (1.55, 1.75), "cd": (2.15, 3.70)},
}

BC_RANGE: tuple[float, float] = (0.30, 0.95)


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    if abs(denominator) < 1e-12:
        return None
    return abs(numerator) / abs(denominator)


def _in_range(value: float | None, bounds: tuple[float, float]) -> bool:
    return value is not None and bounds[0] <= value <= bounds[1]


def _structurally_valid(x: dict, a: dict, b: dict, c: dict, d: dict) -> bool:
    if a["kind"] == x["kind"] or b["kind"] != x["kind"]:
        return False
    if c["kind"] != a["kind"] or d["kind"] != x["kind"]:
        return False
    x_price, a_price = float(x["price"]), float(a["price"])
    b_price = float(b["price"])
    c_price = float(c["price"])
    d_price = float(d["price"])
    if x["kind"] == "low":
        return (
            a_price > x_price
            and x_price < b_price < a_price
            and b_price < c_price < a_price
            and d_price < b_price
        )
    return (
        a_price < x_price
        and x_price > b_price > a_price
        and b_price > c_price > a_price
        and d_price > b_price
    )


def _xd_retracement(x: dict, a: dict, d: dict) -> float | None:
    x_price, a_price, d_price = float(x["price"]), float(a["price"]), float(d["price"])
    if x["kind"] == "low":
        return _safe_ratio(a_price - d_price, a_price - x_price)
    return _safe_ratio(d_price - a_price, x_price - a_price)


def _pattern_score(
    ab: float, bc: float, cd: float, xd: float, spec: dict[str, tuple[float, float]]
) -> float:
    closeness: list[float] = []
    for value, target_bounds in ((ab, spec["ab"]), (xd, spec["xd"]), (cd, spec["cd"])):
        target = (target_bounds[0] + target_bounds[1]) / 2.0
        width = max(target_bounds[1] - target_bounds[0], 1e-9)
        closeness.append(max(0.0, 1.0 - abs(value - target) / width))
    bc_target = (BC_RANGE[0] + BC_RANGE[1]) / 2.0
    bc_width = BC_RANGE[1] - BC_RANGE[0]
    closeness.append(max(0.0, 1.0 - abs(bc - bc_target) / bc_width))
    return round(100.0 * sum(closeness) / len(closeness), 2)


def _point(pivot: dict) -> dict:
    return {
        "index": int(pivot["index"]),
        "price": float(pivot["price"]),
        "kind": pivot["kind"],
        "timestamp": pivot.get("timestamp"),
    }


def _match_window(points: list[dict]) -> dict | None:
    x, a, b, c, d = points
    if not _structurally_valid(x, a, b, c, d):
        return None
    xa = abs(float(a["price"]) - float(x["price"]))
    ab = _safe_ratio(float(b["price"]) - float(a["price"]), xa)
    bc = _safe_ratio(float(c["price"]) - float(b["price"]), float(a["price"]) - float(b["price"]))
    cd = _safe_ratio(float(d["price"]) - float(c["price"]), float(b["price"]) - float(c["price"]))
    xd = _xd_retracement(x, a, d)
    if ab is None or bc is None or cd is None or xd is None:
        return None
    if not _in_range(bc, BC_RANGE):
        return None
    for pattern_type, spec in PATTERN_SPECS.items():
        if (
            _in_range(ab, spec["ab"])
            and _in_range(xd, spec["xd"])
            and _in_range(cd, spec["cd"])
        ):
            return {
                "type": pattern_type,
                "points": {"X": _point(x), "A": _point(a), "B": _point(b), "C": _point(c), "D": _point(d)},
                "ratios": {
                    "xa": round(xa, 6),
                    "ab": round(ab, 6),
                    "bc": round(bc, 6),
                    "cd": round(cd, 6),
                    "xd": round(xd, 6),
                },
                "status": "complete",
                "score": _pattern_score(ab, bc, cd, xd, spec),
            }
    return None


def scan_harmonic(df: pd.DataFrame, *, symbol: str) -> dict:
    patterns: list[dict] = []
    pivots: list[dict] = []
    if len(df) >= MIN_CANDLES:
        prepared = prepare_candles(df)
        pivots = detect_pivots(prepared)
        for start in range(len(pivots) - 4):
            window = pivots[start : start + 5]
            pattern = _match_window(window)
            if pattern is not None:
                patterns.append(pattern)
    return {
        "symbol": symbol,
        "patterns": patterns,
        "pivot_count": len(pivots),
        "pivot_levels": [
            {"index": int(pivot["index"]), "price": float(pivot["price"]), "kind": pivot["kind"]}
            for pivot in pivots
        ],
        "engine_version": ENGINE_VERSION,
    }
