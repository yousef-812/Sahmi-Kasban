from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from sahmi_kasban.fingerprint.models import AccumulationSweepPattern, TimeCyclePattern
from sahmi_kasban.indicators import safe_float


class FingerprintExtractor:
    """Extract statistical time cycle and accumulation sweep patterns from OHLCV data."""

    def extract_time_cycle(self, candles: pd.DataFrame) -> TimeCyclePattern:
        if len(candles) < 60:
            return TimeCyclePattern(
                dominant_cycle_sessions=30,
                stability_score=50.0,
                cycle_phase_sessions=0,
                next_window_in_sessions=5,
            )

        close = candles["close"].to_numpy(dtype=float)
        returns = pd.Series(close).pct_change().fillna(0.0).to_numpy()

        # Compute autocorrelation across lags from 10 to 60 sessions
        max_lag = min(60, len(close) // 3)
        min_lag = 10
        lags = list(range(min_lag, max_lag + 1))
        autocorr_scores: list[tuple[int, float]] = []

        mean_ret = np.mean(returns)
        var_ret = np.var(returns)
        if var_ret > 1e-12:
            norm_ret = returns - mean_ret
            for lag in lags:
                corr = np.sum(norm_ret[lag:] * norm_ret[:-lag]) / (
                    len(norm_ret) * var_ret
                )
                autocorr_scores.append((lag, float(corr)))

        if autocorr_scores:
            best_lag, best_corr = max(autocorr_scores, key=lambda item: item[1])
        else:
            best_lag, best_corr = 30, 0.0

        # Find trough intervals
        lows = candles["low"].to_numpy(dtype=float)
        troughs: list[int] = []
        window = 5
        for i in range(window, len(lows) - window):
            if all(lows[i] <= lows[j] for j in range(i - window, i + window + 1)):
                troughs.append(i)

        if len(troughs) >= 3:
            gaps = [troughs[k] - troughs[k - 1] for k in range(1, len(troughs))]
            mean_gap = float(np.mean(gaps))
            std_gap = float(np.std(gaps))
            stability = max(0.0, min(100.0, 100.0 - (std_gap / (mean_gap + 1e-6)) * 100.0))
            cycle_len = max(10, int(round(mean_gap)))
            last_trough = troughs[-1]
            sessions_since_trough = len(candles) - 1 - last_trough
            next_window = max(1, cycle_len - (sessions_since_trough % cycle_len))
        else:
            cycle_len = max(15, best_lag)
            stability = max(30.0, min(80.0, 50.0 + best_corr * 100.0))
            sessions_since_trough = len(candles) % cycle_len
            next_window = max(1, cycle_len - sessions_since_trough)

        return TimeCyclePattern(
            dominant_cycle_sessions=cycle_len,
            stability_score=round(max(0.0, min(100.0, stability)), 2),
            cycle_phase_sessions=int(sessions_since_trough),
            next_window_in_sessions=int(next_window),
        )

    def extract_accumulation_sweep(self, candles: pd.DataFrame) -> AccumulationSweepPattern:
        if len(candles) < 40:
            return AccumulationSweepPattern()

        highs = candles["high"].to_numpy(dtype=float)
        lows = candles["low"].to_numpy(dtype=float)
        closes = candles["close"].to_numpy(dtype=float)

        sweeps: list[dict[str, float]] = []

        for i in range(20, len(candles) - 5):
            prior_low = float(np.min(lows[i - 20 : i]))
            current_low = lows[i]
            current_close = closes[i]

            if current_low < prior_low and current_close > current_low:
                sweep_depth_pct = (prior_low - current_low) / prior_low * 100.0
                if 0.2 <= sweep_depth_pct <= 10.0:
                    subsequent_max = float(np.max(highs[i + 1 : i + 6]))
                    gain_pct = (subsequent_max / current_close - 1.0) * 100.0
                    success = gain_pct >= 2.5

                    # Calculate velocity (sessions to reach max high)
                    max_idx = int(np.argmax(highs[i + 1 : i + 6])) + 1

                    sweeps.append(
                        {
                            "sweep_depth_pct": sweep_depth_pct,
                            "success": 1.0 if success else 0.0,
                            "velocity": float(max_idx),
                        }
                    )

        if not sweeps:
            return AccumulationSweepPattern()

        avg_depth = float(np.mean([s["sweep_depth_pct"] for s in sweeps]))
        bounce_prob = float(np.mean([s["success"] for s in sweeps])) * 100.0
        avg_velocity = int(round(float(np.mean([s["velocity"] for s in sweeps]))))

        # Estimate FVG fill preference (average retracement % into recent gaps)
        fvg_fills: list[float] = []
        for i in range(2, len(candles)):
            if lows[i] > highs[i - 2]:  # Bullish FVG
                gap_size = lows[i] - highs[i - 2]
                if gap_size > 0:
                    # check how deep subsequent candles dipped into the gap
                    end_idx = min(len(candles), i + 10)
                    dip = float(np.min(lows[i:end_idx]))
                    fill_pct = max(0.0, min(100.0, (lows[i] - dip) / gap_size * 100.0))
                    fvg_fills.append(fill_pct)

        fvg_pref = float(np.mean(fvg_fills)) if fvg_fills else 50.0

        return AccumulationSweepPattern(
            avg_sweep_depth_pct=round(max(0.1, min(15.0, avg_depth)), 2),
            bounce_probability_pct=round(max(0.0, min(100.0, bounce_prob)), 2),
            avg_velocity_sessions=max(1, min(15, avg_velocity)),
            fvg_fill_preference_pct=round(max(0.0, min(100.0, fvg_pref)), 2),
        )
