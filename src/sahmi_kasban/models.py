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
    min_average_turnover: float = 1_000_000.0
    atr_min_pct: float = 0.5
    atr_max_pct: float = 8.0
    min_qualification_score: float = 55.0
    stop_atr_multiple: float = 2.0
    max_stop_atr_multiple: float = 4.0
    target_1_r: float = 2.0
    target_2_r: float = 3.5
    liquidity_participation_rate: float = 0.01
    support_lookback: int = 20
    buy_score_threshold: float = 67.0
    avoid_score_threshold: float = 42.0
    min_buy_risk_score: float = 50.0
    min_buy_confidence: float = 65.0
    max_buy_engine_dispersion: float = 22.0
    backtest_horizon: int = 5

    def __post_init__(self) -> None:
        if self.capital <= 0:
            raise ValueError("capital must be positive")
        if not 0 < self.risk_per_trade <= 0.10:
            raise ValueError("risk_per_trade must be between 0 and 0.10")
        if self.max_position_value <= 0:
            raise ValueError("max_position_value must be positive")
        if self.max_positions <= 0:
            raise ValueError("max_positions must be positive")
        if self.min_history < 40:
            raise ValueError("min_history must be at least 40")
        if self.min_average_volume < 0 or self.min_average_turnover < 0:
            raise ValueError("liquidity thresholds cannot be negative")
        if self.atr_min_pct < 0 or self.atr_max_pct <= self.atr_min_pct:
            raise ValueError("invalid ATR range")
        if self.stop_atr_multiple <= 0:
            raise ValueError("stop_atr_multiple must be positive")
        if self.max_stop_atr_multiple < self.stop_atr_multiple:
            raise ValueError("max_stop_atr_multiple cannot be below stop_atr_multiple")
        if not 0 < self.liquidity_participation_rate <= 0.10:
            raise ValueError("liquidity_participation_rate must be between 0 and 0.10")
        if self.support_lookback < 5:
            raise ValueError("support_lookback must be at least 5")
        if not 0 <= self.avoid_score_threshold < self.buy_score_threshold <= 100:
            raise ValueError("invalid signal score thresholds")
        if not 0 <= self.min_buy_risk_score <= 100:
            raise ValueError("min_buy_risk_score must be between 0 and 100")
        if not 0 <= self.min_buy_confidence <= 100:
            raise ValueError("min_buy_confidence must be between 0 and 100")
        if self.max_buy_engine_dispersion <= 0:
            raise ValueError("max_buy_engine_dispersion must be positive")
        if self.backtest_horizon < 1:
            raise ValueError("backtest_horizon must be positive")


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
    diagnostics: dict[str, Any] = field(default_factory=dict)

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
            "diagnostics": dict(self.diagnostics),
        }
