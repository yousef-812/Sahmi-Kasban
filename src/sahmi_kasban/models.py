from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Signal = Literal["BUY", "WATCH", "AVOID"]
EngineStatus = Literal["complete", "rejected", "error"]


@dataclass(slots=True)
class AnalysisConfig:
    capital: float = 150_000.0
    risk_per_trade: float = 0.01
    max_position_value: float = 40_000.0
    max_positions: int = 4
    min_history: int = 60
    min_average_volume: float = 100_000.0
    min_average_turnover_egp: float = 1_000_000.0
    atr_min_pct: float = 0.5
    atr_max_pct: float = 8.0
    min_qualification_score: float = 50.0
    stop_atr_multiple: float = 2.0
    target_1_r: float = 1.0
    target_2_r: float = 1.75
    # Opportunity quality & tuning thresholds
    elite_min_directional_score: float = 80.0
    elite_min_confidence: float = 70.0
    balanced_max_return_20d_pct: float = 30.0
    balanced_base_max_atr_pct: float = 4.5
    balanced_base_max_total_risk_pct: float = 30.0
    aggressive_min_return_20d_pct: float = 5.0
    aggressive_max_return_20d_pct: float = 45.0
    aggressive_max_return_5d_pct: float = 15.0
    aggressive_min_breakout_pct: float = 2.0
    aggressive_max_breakout_pct: float = 12.0
    aggressive_min_volume_ratio: float = 2.0
    aggressive_min_turnover_egp: float = 5_000_000.0
    elite_max_zero_volume_ratio: float = 0.10
    aggressive_max_zero_volume_ratio: float = 0.05
    # Signal thresholds
    signal_buy_score_threshold: float = 67.0
    signal_buy_risk_threshold: float = 50.0
    signal_avoid_score_threshold: float = 42.0
    signal_avoid_risk_threshold: float = 35.0
    # SMC Order Block thresholds
    smc_ob_displacement_multiplier: float = 1.5
    smc_ob_volume_multiplier: float = 1.0

    def __post_init__(self) -> None:
        if self.capital <= 0:
            raise ValueError("capital must be positive")
        if not 0 < self.risk_per_trade <= 0.10:
            raise ValueError("risk_per_trade must be between 0 and 0.10")
        if self.max_position_value <= 0:
            raise ValueError("max_position_value must be positive")
        if self.min_average_volume < 0:
            raise ValueError("min_average_volume cannot be negative")
        if self.min_average_turnover_egp < 0:
            raise ValueError("min_average_turnover_egp cannot be negative")
        if self.atr_min_pct < 0 or self.atr_max_pct <= self.atr_min_pct:
            raise ValueError("invalid ATR range")
        if self.target_1_r <= 0 or self.target_2_r <= self.target_1_r:
            raise ValueError("reward targets must be positive and increasing")


@dataclass(slots=True)
class EngineResult:
    name: str
    score: float
    confidence: float
    status: EngineStatus = "complete"
    details: dict[str, Any] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.score = round(max(0.0, min(100.0, float(self.score))), 2)
        self.confidence = round(max(0.0, min(100.0, float(self.confidence))), 2)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TradePlan:
    entry: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_per_share: float
    reward_risk_1: float
    reward_risk_2: float
    position_size: int
    position_value: float
    risk_amount: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AnalysisReport:
    ticker: str
    signal: Signal
    final_score: float
    confidence: float
    qualified: bool
    engines: dict[str, EngineResult]
    trade_plan: TradePlan | None = None
    warnings: list[str] = field(default_factory=list)
    analysis_quality: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "signal": self.signal,
            "final_score": self.final_score,
            "confidence": self.confidence,
            "qualified": self.qualified,
            "engines": {name: result.to_dict() for name, result in self.engines.items()},
            "trade_plan": self.trade_plan.to_dict() if self.trade_plan else None,
            "warnings": list(self.warnings),
            "analysis_quality": dict(self.analysis_quality),
        }
