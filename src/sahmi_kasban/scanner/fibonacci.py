from __future__ import annotations

import pandas as pd

from sahmi_kasban.indicators import ema, enrich_indicators, prepare_candles, safe_float
from sahmi_kasban.scanner.swings import detect_pivots, latest_impulse

MIN_CANDLES = 20

FIB_LEVELS: tuple[tuple[str, float, str, str], ...] = (
    ("23.6", 0.236, "23.6%", "23.6%"),
    ("38.2", 0.382, "38.2%", "38.2%"),
    ("50", 0.5, "50%", "50%"),
    ("61.8", 0.618, "61.8%", "61.8%"),
    ("78.6", 0.786, "78.6%", "78.6%"),
)

GOLDEN_ZONE: tuple[float, float] = (61.8, 65.0)


def _anchor(pivot: dict) -> dict:
    timestamp = pivot.get("timestamp")
    date = None
    if timestamp is not None:
        date = pd.Timestamp(timestamp).date().isoformat()
    return {
        "kind": pivot["kind"],
        "index": int(pivot["index"]),
        "price": safe_float(pivot["price"]),
        "timestamp": timestamp,
        "date": date,
    }


def _retracement_percent(direction: str, start_price: float, end_price: float, price: float) -> float:
    span = end_price - start_price
    if abs(span) < 1e-12:
        return 0.0
    if direction == "up":
        return (end_price - price) / span * 100.0
    return (price - end_price) / span * 100.0


def _level_price(direction: str, start_price: float, end_price: float, ratio: float) -> float:
    if direction == "up":
        return end_price - ratio * (end_price - start_price)
    return end_price + ratio * (start_price - end_price)


def _classify_zone(
    retracement_percent: float,
    direction: str,
    start_price: float,
    end_price: float,
    price: float,
) -> dict:
    if retracement_percent < 0.0:
        price_low, price_high = sorted((end_price, price))
        return {
            "kind": "extension",
            "key": "extension",
            "labelAr": "امتداد فوق نهاية الحركة",
            "labelEn": "Impulse Extension",
            "priceLow": price_low,
            "priceHigh": price_high,
        }
    if retracement_percent > 100.0:
        price_low, price_high = sorted((start_price, price))
        return {
            "kind": "beyond",
            "key": "beyond",
            "labelAr": "تجاوز مستوى البداية 100%",
            "labelEn": "Beyond 100% Level",
            "priceLow": price_low,
            "priceHigh": price_high,
        }
    bounds: tuple[tuple[str, str, float, float, str, str], ...] = (
        ("0-23.6", "retracement", 0.0, 23.6, "منطقة 0% – 23.6%", "Zone 0% - 23.6%"),
        ("23.6-38.2", "retracement", 23.6, 38.2, "منطقة 23.6% – 38.2%", "Zone 23.6% - 38.2%"),
        ("38.2-50", "retracement", 38.2, 50.0, "منطقة 38.2% – 50%", "Zone 38.2% - 50%"),
        ("50-61.8", "retracement", 50.0, 61.8, "منطقة 50% – 61.8%", "Zone 50% - 61.8%"),
        ("golden", "golden", 61.8, 65.0, "المنطقة الذهبية", "Golden Zone"),
        ("65-78.6", "retracement", 65.0, 78.6, "منطقة 65% – 78.6%", "Zone 65% - 78.6%"),
        ("78.6-100", "retracement", 78.6, 100.0, "منطقة 78.6% – 100%", "Zone 78.6% - 100%"),
    )
    for index, (key, kind, low, high, label_ar, label_en) in enumerate(bounds):
        is_last = index == len(bounds) - 1
        if kind == "golden" or is_last:
            in_zone = low <= retracement_percent <= high
        else:
            in_zone = low <= retracement_percent < high
        if in_zone:
            return {
                "kind": kind,
                "key": key,
                "labelAr": label_ar,
                "labelEn": label_en,
                "priceLow": _level_price(direction, start_price, end_price, high / 100.0),
                "priceHigh": _level_price(direction, start_price, end_price, low / 100.0),
            }
    return {
        "kind": "retracement",
        "key": "78.6-100",
        "labelAr": "منطقة 78.6% – 100%",
        "labelEn": "Zone 78.6% - 100%",
        "priceLow": _level_price(direction, start_price, end_price, 1.0),
        "priceHigh": _level_price(direction, start_price, end_price, 0.786),
    }


def _levels(direction: str, start_price: float, end_price: float, price: float) -> list[dict]:
    levels: list[dict] = []
    for key, ratio, label_ar, label_en in FIB_LEVELS:
        level_price = _level_price(direction, start_price, end_price, ratio)
        levels.append(
            {
                "key": key,
                "kind": "resistance" if price <= level_price else "support",
                "ratio": ratio,
                "price": level_price,
                "labelAr": f"مستوى فيبوناتشي {label_ar}",
                "labelEn": f"Fibonacci {label_en}",
            }
        )
    return levels


def _status(retracement_percent: float, price: float, levels: list[dict], atr14: float) -> str:
    if retracement_percent < 0.0 or retracement_percent > 100.0:
        return "broken"
    nearest = min(abs(price - float(level["price"])) for level in levels)
    reference = atr14 if atr14 > 0 else max(price * 0.01, 1e-9)
    if nearest <= reference:
        return "testing"
    return "approaching"


def _nearest_distance(price: float, levels: list[dict]) -> float:
    return min(abs(price - float(level["price"])) for level in levels)


def scan_fibonacci(df: pd.DataFrame, *, symbol: str, meta: dict | None = None) -> dict | None:
    prepared = prepare_candles(df)
    if len(prepared) < MIN_CANDLES:
        return None
    enriched = enrich_indicators(prepared)
    latest = enriched.iloc[-1]
    price = safe_float(latest["close"])

    pivots = detect_pivots(prepared)
    impulse = latest_impulse(pivots)
    if impulse is None:
        return None
    start_pivot, end_pivot = impulse
    start_price = safe_float(start_pivot["price"])
    end_price = safe_float(end_pivot["price"])
    if abs(end_price - start_price) < 1e-12:
        return None
    direction = "up" if end_price > start_price else "down"

    atr14 = safe_float(latest.get("atr"), price * 0.02)
    ema_20 = safe_float(ema(enriched["close"], 20).iloc[-1])
    ema_50 = safe_float(ema(enriched["close"], 50).iloc[-1])
    rsi14 = safe_float(latest.get("rsi"))
    relative_volume20 = safe_float(latest.get("relative_volume_20"), 1.0)
    turnover = price * safe_float(latest.get("volume"))

    retracement_percent = _retracement_percent(direction, start_price, end_price, price)
    swing_percent = abs(end_price - start_price) / start_price * 100.0 if start_price > 0 else 0.0
    swing_atr = abs(end_price - start_price) / atr14 if atr14 > 0 else 0.0

    levels = _levels(direction, start_price, end_price, price)
    current_zone = _classify_zone(retracement_percent, direction, start_price, end_price, price)
    status = _status(retracement_percent, price, levels, atr14)

    trend_aligned = int(
        (direction == "up" and ema_20 > ema_50) or (direction == "down" and ema_20 < ema_50)
    )

    nearest = _nearest_distance(price, levels)
    in_range = 0.0 <= retracement_percent <= 100.0
    score = 40.0
    if current_zone["kind"] == "golden":
        score += 20.0
    if status == "testing":
        score += 15.0
    elif status == "approaching":
        score += 8.0
    if trend_aligned:
        score += 15.0
    if relative_volume20 >= 1.3:
        score += 10.0
    elif relative_volume20 >= 1.0:
        score += 5.0
    score += 5.0 if in_range else -15.0
    score = round(max(0.0, min(100.0, score)), 2)

    confidence = 35.0 + min(30.0, swing_atr * 4.0)
    confidence += 10.0 if trend_aligned else 0.0
    if status == "testing":
        confidence += 10.0
    elif status == "approaching":
        confidence += 4.0
    confidence = round(max(0.0, min(95.0, confidence)), 2)

    meta_data = meta or {}
    return {
        "symbol": symbol,
        "nameAr": meta_data.get("nameAr"),
        "sector": meta_data.get("sector"),
        "price": price,
        "direction": direction,
        "timeframe": str(meta_data.get("timeframe", "1D")),
        "anchorStart": _anchor(start_pivot),
        "anchorEnd": _anchor(end_pivot),
        "swingPercent": round(swing_percent, 4),
        "swingAtr": round(swing_atr, 4),
        "retracementPercent": round(retracement_percent, 4),
        "currentZone": current_zone,
        "distancePercent": round(nearest / price * 100.0 if price > 0 else 0.0, 4),
        "distanceAtr": round(nearest / atr14 if atr14 > 0 else 0.0, 4),
        "status": status,
        "score": score,
        "confidence": confidence,
        "trendAligned": trend_aligned,
        "metrics": {
            "atr14": round(atr14, 4),
            "ema20": round(ema_20, 4),
            "ema50": round(ema_50, 4),
            "rsi14": round(rsi14, 4),
            "relativeVolume20": round(relative_volume20, 4),
            "turnover": round(turnover, 4),
        },
        "levels": levels,
    }
