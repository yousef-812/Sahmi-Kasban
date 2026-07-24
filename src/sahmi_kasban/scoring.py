from __future__ import annotations

from collections.abc import Mapping

from sahmi_kasban.models import EngineResult, Signal

DEFAULT_WEIGHTS: dict[str, float] = {
    "stock_qualification": 0.08,
    "market_environment": 0.12,
    "technical": 0.22,
    "smc": 0.18,
    "multi_timeframe": 0.14,
    "quantitative": 0.14,
    "risk": 0.12,
}


def calculate_final_score(
    engines: Mapping[str, EngineResult],
    weights: Mapping[str, float] | None = None,
) -> tuple[float, float]:
    selected_weights = dict(weights or DEFAULT_WEIGHTS)
    weighted_score = 0.0
    weighted_confidence = 0.0
    used_weight = 0.0

    for name, weight in selected_weights.items():
        result = engines.get(name)
        if result is None or result.status == "error" or weight <= 0:
            continue
        weighted_score += result.score * weight
        weighted_confidence += result.confidence * weight
        used_weight += weight

    if used_weight <= 0:
        return 0.0, 0.0
    return round(weighted_score / used_weight, 2), round(weighted_confidence / used_weight, 2)


def score_to_signal(score: float, qualified: bool, risk_score: float) -> Signal:
    if not qualified or risk_score < 35 or score < 42:
        return "AVOID"
    if score >= 67 and risk_score >= 50:
        return "BUY"
    return "WATCH"
