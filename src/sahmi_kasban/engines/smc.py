from __future__ import annotations

import pandas as pd

from sahmi_kasban.engines.base import AnalysisEngine
from sahmi_kasban.indicators import safe_float
from sahmi_kasban.models import EngineResult


def _detect_swing_points(candles: pd.DataFrame, window: int) -> list[dict[str, object]]:
    """Detect swing highs and swing lows using a local extremum window.

    Returns a list of dicts: ``{price, kind, avg_volume, touches}`` where
    ``kind`` is either "high" (resistance) or "low" (support). A swing point's
    supporting volume is the modal candle volume within its neighbourhood so a
    level is strong only when it was defended by real volume.
    """
    points: list[dict[str, object]] = []
    n = len(candles)
    if n - 2 * window < 1:
        return points

    highs = candles["high"].to_numpy(dtype=float)
    lows = candles["low"].to_numpy(dtype=float)
    volumes = candles["volume"].to_numpy(dtype=float)
    if "avg_volume_20" in candles.columns:
        avg_volume_20 = candles["avg_volume_20"].to_numpy(dtype=float)
    else:
        avg_volume_20 = (
            pd.Series(volumes).rolling(20, min_periods=5).mean().to_numpy(dtype=float)
        )
        avg_volume_20 = [v if v == v else volumes[i] for i, v in enumerate(avg_volume_20)]

    for i in range(window, n - window):
        hi = highs[i]
        lo = lows[i]
        is_swing_high = all(
            not pd.isna(highs[j]) and hi >= highs[j] for j in range(i - window, i + window + 1)
        )
        if is_swing_high:
            # Volume that "defended" this high: candles near the level with volume.
            level_volumes = [
                volumes[j]
                for j in range(i - window, i + window + 1)
                if highs[j] and abs(highs[j] - hi) / hi <= 0.005
            ]
            base_avg = avg_volume_20[i]
            avg_vol = (
                sum(level_volumes) / len(level_volumes)
                if level_volumes
                else volumes[i]
            )
            points.append(
                {
                    "price": hi,
                    "kind": "high",
                    "volume": avg_vol,
                    "base_volume": base_avg if not pd.isna(base_avg) and base_avg > 0 else volumes[i],
                }
            )
        is_swing_low = all(
            not pd.isna(lows[j]) and lo <= lows[j] for j in range(i - window, i + window + 1)
        )
        if is_swing_low:
            level_volumes = [
                volumes[j]
                for j in range(i - window, i + window + 1)
                if lows[j] and abs(lows[j] - lo) / lo <= 0.005
            ]
            base_avg = avg_volume_20[i]
            avg_vol = (
                sum(level_volumes) / len(level_volumes)
                if level_volumes
                else volumes[i]
            )
            points.append(
                {
                    "price": lo,
                    "kind": "low",
                    "volume": avg_vol,
                    "base_volume": base_avg if not pd.isna(base_avg) and base_avg > 0 else volumes[i],
                }
            )
    return points


def _cluster_zones(points: list[dict[str, object]], bucket_pct: float) -> list[dict[str, object]]:
    """Cluster nearby swing points of the same kind into price zones.

    Two swing points belong to the same zone when their prices are within
    ``bucket_pct`` of each other. Each zone aggregates the touch count and the
    median supporting volume so a repeated, heavily-traded level reads as strong.
    """
    zones: list[dict[str, object]] = []
    for point in sorted(points, key=lambda p: float(p["price"])):
        price = float(point["price"])
        kind = point["kind"]
        volume = float(point["volume"])
        base_volume = float(point["base_volume"])
        placed = False
        for zone in zones:
            if zone["kind"] != kind:
                continue
            zone_price = float(zone["price"])
            if abs(price - zone_price) / zone_price <= bucket_pct:
                touches = int(zone["touches"]) + 1
                zone["touches"] = touches
                zone["volume_sum"] = float(zone["volume_sum"]) + volume
                zone["volume_counts"].append(volume)
                zone["base_volumes"].append(base_volume)
                weighted = (float(zone["price"]) * (touches - 1) + price) / touches
                zone["price"] = round(weighted, 4)
                # confidence of the zone (shared touches across close levels)
                zone["confidence"] = 40.0 + min(55.0, touches * 12.0)
                placed = True
                break
        if not placed:
            zones.append(
                {
                    "price": price,
                    "kind": kind,
                    "touches": 1,
                    "volume_sum": volume,
                    "volume_counts": [volume],
                    "base_volumes": [base_volume],
                    "confidence": 40.0,
                }
            )
    return zones


class SMCEngine(AnalysisEngine):
    name = "smc"

    def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult:
        recent = candles.tail(min(60, len(candles))).copy()
        latest = recent.iloc[-1]
        close = safe_float(latest["close"])
        atr_value = safe_float(latest.get("atr"), close * 0.02)
        range_prox_atr = max(atr_value * 0.5, close * 0.003)

        previous_20 = recent.iloc[-21:-1] if len(recent) >= 21 else recent.iloc[:-1]
        previous_10 = recent.iloc[-11:-1] if len(recent) >= 11 else recent.iloc[:-1]
        high_20 = safe_float(previous_20["high"].max(), close)
        low_20 = safe_float(previous_20["low"].min(), close)
        high_10 = safe_float(previous_10["high"].max(), close)
        low_10 = safe_float(previous_10["low"].min(), close)

        bullish_bos = close > high_20 if not previous_20.empty else False
        bearish_bos = close < low_20 if not previous_20.empty else False

        prior_trend_up = False
        if len(recent) >= 25:
            earlier = recent.iloc[-25:-10]
            later = recent.iloc[-10:]
            prior_trend_up = later["close"].mean() > earlier["close"].mean()
        choch = (prior_trend_up and bearish_bos) or (not prior_trend_up and bullish_bos)

        latest_low = safe_float(latest["low"])
        latest_high = safe_float(latest["high"])
        liquidity_sweep_low = latest_low < low_10 and close > low_10
        liquidity_sweep_high = latest_high > high_10 and close < high_10

        fvg_bullish = False
        fvg_bearish = False
        if len(recent) >= 3:
            first = recent.iloc[-3]
            third = recent.iloc[-1]
            fvg_bullish = safe_float(third["low"]) > safe_float(first["high"])
            fvg_bearish = safe_float(third["high"]) < safe_float(first["low"])

        range_size = max(high_20 - low_20, 1e-9)
        range_position = (close - low_20) / range_size
        zone = (
            "discount"
            if range_position <= 0.45
            else "premium"
            if range_position >= 0.55
            else "equilibrium"
        )

        body = (recent["close"] - recent["open"]).abs()
        body_median = safe_float(body.tail(20).median())
        volume_avg = safe_float(recent["volume"].tail(20).mean())
        displacement_mult = getattr(self.config, "smc_ob_displacement_multiplier", 1.5)
        volume_mult = getattr(self.config, "smc_ob_volume_multiplier", 1.0)

        bullish_order_blocks: list[dict[str, float]] = []
        bearish_order_blocks: list[dict[str, float]] = []
        for index in range(max(1, len(recent) - 12), len(recent) - 1):
            candle = recent.iloc[index]
            next_candle = recent.iloc[index + 1]
            candle_close = safe_float(candle["close"])
            candle_open = safe_float(candle["open"])
            candle_high = safe_float(candle["high"])
            candle_low = safe_float(candle["low"])
            candle_body = abs(candle_close - candle_open)

            next_close = safe_float(next_candle["close"])
            next_open = safe_float(next_candle["open"])
            next_volume = safe_float(next_candle["volume"])
            next_avg_vol = safe_float(next_candle.get("avg_volume_20"), volume_avg)
            displacement = abs(next_close - next_open)

            volume_confirmed = next_volume >= next_avg_vol * volume_mult

            if (
                candle_body <= body_median
                and displacement >= body_median * displacement_mult
                and volume_confirmed
            ):
                block = {
                    "low": round(candle_low, 4),
                    "high": round(candle_high, 4),
                }
                # Bullish OB: prev red, next green, next closes ABOVE prev high
                if (
                    candle_close < candle_open
                    and next_close > next_open
                    and next_close > candle_high
                ):
                    bullish_order_blocks.append(block)
                # Bearish OB: prev green, next red, next closes BELOW prev low
                elif (
                    candle_close > candle_open
                    and next_close < next_open
                    and next_close < candle_low
                ):
                    bearish_order_blocks.append(block)

        # ---- Support / Resistance analysis over the full history ----
        sr_cfg = self.config
        bucket_pct = getattr(sr_cfg, "sr_zone_bucket_pct", 0.35) / 100.0
        min_touches = int(getattr(sr_cfg, "sr_min_touches", 2))
        strong_res_touches = int(getattr(sr_cfg, "sr_strong_resistance_touches", 3))
        strong_vol_mult = getattr(sr_cfg, "sr_strong_volume_mult", 1.2)
        proximity_pct = getattr(sr_cfg, "sr_resistance_proximity_pct", 1.0) / 100.0
        resistance_penalty = float(getattr(sr_cfg, "sr_resistance_penalty", 26.0))
        support_bonus = float(getattr(sr_cfg, "sr_support_bonus", 8.0))

        swing_points = _detect_swing_points(candles, window=3)
        zones = _cluster_zones(swing_points, bucket_pct)

        resistance_zones = [
            z
            for z in zones
            if z["kind"] == "high" and int(z["touches"]) >= min_touches
        ]
        support_zones = [
            z
            for z in zones
            if z["kind"] == "low" and int(z["touches"]) >= min_touches
        ]

        # Nearest resistance above the current price.
        resistances_above = [
            z for z in resistance_zones if float(z["price"]) > close + range_prox_atr
        ]
        nearest_resistance = (
            min(resistances_above, key=lambda z: float(z["price"]))
            if resistances_above
            else None
        )
        supports_below = [
            z for z in support_zones if float(z["price"]) < close - range_prox_atr
        ]
        nearest_support = (
            max(supports_below, key=lambda z: float(z["price"]))
            if supports_below
            else None
        )

        def _zone_strong(z: dict[str, object]) -> bool:
            touches = int(z["touches"])
            counts = z.get("volume_counts") or []
            bases = z.get("base_volumes") or []
            vols = [(c, b) for c, b in zip(counts, bases, strict=False) if b and b > 0 and c and c > 0]
            rel_vol = (sum(v for v, _ in vols) / len(vols)) if vols else 0.0
            base = max(1e-9, sum(b for _, b in vols) / len(vols)) if vols else 1.0
            volume_strong = rel_vol >= base * strong_vol_mult
            return touches >= strong_res_touches and volume_strong

        near_strong_resistance = False
        if nearest_resistance is not None:
            res_price = float(nearest_resistance["price"])
            distance_pct = (res_price - close) / close if close > 0 else 1.0
            near_strong_resistance = (
                distance_pct <= proximity_pct and _zone_strong(nearest_resistance)
            )

        support_strength = 0.0
        if nearest_support is not None:
            sup_price = float(nearest_support["price"])
            distance_pct = (close - sup_price) / close if close > 0 else 0.0
            touched = int(nearest_support["touches"])
            counts = nearest_support.get("volume_counts") or []
            bases = nearest_support.get("base_volumes") or []
            vols = [(c, b) for c, b in zip(counts, bases, strict=False) if b and b > 0 and c and c > 0]
            rel_vol = (sum(v for v, _ in vols) / len(vols)) if vols else 0.0
            base = max(1e-9, sum(b for _, b in vols) / len(vols)) if vols else 1.0
            volume_ratio = rel_vol / base
            # Support is strongest when the price is sitting just above it with
            # volume defending it.
            within = distance_pct <= proximity_pct * 3
            support_strength = (
                min(0.5, touched / 8.0)
                + min(0.35, max(0.0, volume_ratio - 1.0))
            )
            support_strength = support_strength if within else support_strength * 0.5

        score = 50.0
        reasons: list[str] = []
        if bullish_bos:
            score += 18
            reasons.append("Bullish break of structure")
        if bearish_bos:
            score -= 18
            reasons.append("Bearish break of structure")
        if liquidity_sweep_low:
            score += 12
            reasons.append("Sell-side liquidity sweep")
        if liquidity_sweep_high:
            score -= 10
            reasons.append("Buy-side liquidity sweep")
        if fvg_bullish:
            score += 7
            reasons.append("Bullish fair value gap")
        if fvg_bearish:
            score -= 7
            reasons.append("Bearish fair value gap")
        if zone == "discount":
            score += 8
            reasons.append("Price in discount zone")
        elif zone == "premium":
            score -= 5
        if bullish_order_blocks:
            score += min(8, len(bullish_order_blocks) * 3)
        if bearish_order_blocks:
            score -= min(8, len(bearish_order_blocks) * 3)

        # ---- Support / Resistance score contribution (core pillar) ----
        sr_details: dict[str, object] = {}
        if near_strong_resistance:
            score -= resistance_penalty
            reasons.append("Price is under a strong high-volume resistance")
        elif nearest_resistance is not None:
            res_price = float(nearest_resistance["price"])
            distance_pct = (res_price - close) / close if close > 0 else 1.0
            if distance_pct <= proximity_pct * 2.5:
                score -= 6
                reasons.append("Price is near a resistance level")
        if nearest_support is not None:
            score += support_bonus * min(1.0, support_strength)
            if support_strength >= 0.5:
                reasons.append("Price rests above a strong volume support")

        score = self.clamp(score)

        if near_strong_resistance:
            sr_details = {
                "near_strong_resistance": True,
                "resistance_penalty": resistance_penalty,
            }
        else:
            sr_details = {"near_strong_resistance": False}

        context["smc_bias"] = (
            "bullish" if score >= 60 else "bearish" if score <= 40 else "neutral"
        )
        return EngineResult(
            name=self.name,
            score=score,
            confidence=min(92.0, 55.0 + len(reasons) * 6),
            details={
                "bullish_bos": bullish_bos,
                "bearish_bos": bearish_bos,
                "choch": choch,
                "liquidity_sweep_low": liquidity_sweep_low,
                "liquidity_sweep_high": liquidity_sweep_high,
                "fvg_bullish": fvg_bullish,
                "fvg_bearish": fvg_bearish,
                "range_position": round(range_position, 3),
                "zone": zone,
                "bullish_order_blocks": bullish_order_blocks[-3:],
                "bearish_order_blocks": bearish_order_blocks[-3:],
                "support_resistance": {
                    "nearest_resistance": (
                        {
                            "price": round(float(nearest_resistance["price"]), 4),
                            "touches": int(nearest_resistance["touches"]),
                            "strong": _zone_strong(nearest_resistance),
                        }
                        if nearest_resistance is not None
                        else None
                    ),
                    "nearest_support": (
                        {
                            "price": round(float(nearest_support["price"]), 4),
                            "touches": int(nearest_support["touches"]),
                            "distance_pct": round(
                                (close - float(nearest_support["price"]))
                                / close
                                * 100.0
                                if close > 0
                                else 0.0,
                                2,
                            ),
                            "strength": round(support_strength, 2),
                        }
                        if nearest_support is not None
                        else None
                    ),
                    "near_strong_resistance": near_strong_resistance,
                    "resistance_proximity_pct": round(proximity_pct * 100.0, 2),
                    "zone_count": len(zones),
                },
                **sr_details,
            },
            reasons=reasons,
        )
