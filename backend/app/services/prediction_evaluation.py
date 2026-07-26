from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.market_calendar import EGXTradingCalendar
from app.market_data.types import CandleSeries
from app.models import Discussion, PredictionVerification
from app.services.wallet import credit_points, get_wallet_account

PERIOD_SESSION_COUNTS = {
    "next_session": 1,
    "week": 5,
    "month": 20,
}
PREDICTION_REWARD_ENTRY_TYPE = "prediction_verification_reward"
ALGORITHM_VERSION = "phase7_v1"


class PredictionEvaluationError(RuntimeError):
    """Base error for server-authoritative prediction evaluation."""


class PredictionNotFoundError(PredictionEvaluationError):
    """Raised when the prediction does not belong to the requesting user."""


class PredictionUnavailableError(PredictionEvaluationError):
    """Raised when a discussion cannot be evaluated."""


class PredictionMarketEvidenceError(PredictionEvaluationError):
    """Raised when final market candles are incomplete or invalid."""


class PredictionNotEligibleError(PredictionEvaluationError):
    """Raised when the target period has not finished yet."""

    def __init__(self, eligible_at: datetime) -> None:
        self.eligible_at = eligible_at
        super().__init__(
            f"Prediction can be verified after {eligible_at.isoformat()}"
        )


@dataclass(frozen=True, slots=True)
class PredictionWindow:
    session_dates: tuple[date, ...]
    eligible_at: datetime

    @property
    def start_session_date(self) -> date:
        return self.session_dates[0]

    @property
    def end_session_date(self) -> date:
        return self.session_dates[-1]


@dataclass(frozen=True, slots=True)
class PredictionStatus:
    discussion: Discussion
    verification: PredictionVerification | None
    state: str
    window: PredictionWindow | None


@dataclass(frozen=True, slots=True)
class PredictionScore:
    score_bp: int
    strength: str
    reward_points: int
    market_outcome: dict[str, Any]
    evidence: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PredictionVerificationResult:
    verification: PredictionVerification
    balance_points: int
    idempotent: bool


@dataclass(frozen=True, slots=True)
class PredictionStats:
    verified_predictions: int
    accepted_predictions: int
    average_score_bp: int
    total_reward_points: int


def _aware(moment: datetime) -> datetime:
    if moment.tzinfo is None:
        return moment.replace(tzinfo=UTC)
    return moment.astimezone(UTC)


def _current(moment: datetime | None = None) -> datetime:
    return _aware(moment or datetime.now(UTC))


def resolve_prediction_window(
    discussion: Discussion,
    *,
    calendar: EGXTradingCalendar | None = None,
) -> PredictionWindow:
    if discussion.published_at is None:
        raise PredictionUnavailableError("Discussion does not have a publication time")
    session_count = PERIOD_SESSION_COUNTS.get(discussion.period_type)
    if session_count is None:
        raise PredictionUnavailableError("Discussion period is not supported")

    trading_calendar = calendar or EGXTradingCalendar.from_settings()
    published_local_date = _aware(discussion.published_at).astimezone(
        trading_calendar.timezone
    ).date()
    session_dates = [trading_calendar.next_trading_session(published_local_date)]
    while len(session_dates) < session_count:
        session_dates.append(
            trading_calendar.next_trading_session(session_dates[-1])
        )

    eligible_local = datetime.combine(
        session_dates[-1],
        trading_calendar.scan_time,
        tzinfo=trading_calendar.timezone,
    )
    return PredictionWindow(
        session_dates=tuple(session_dates),
        eligible_at=eligible_local.astimezone(UTC),
    )


def get_prediction_status(
    db: Session,
    *,
    discussion_id: UUID,
    user_id: UUID,
    moment: datetime | None = None,
    calendar: EGXTradingCalendar | None = None,
) -> PredictionStatus:
    discussion = db.scalar(
        select(Discussion).where(
            Discussion.id == discussion_id,
            Discussion.user_id == user_id,
        )
    )
    if discussion is None:
        raise PredictionNotFoundError("Discussion does not exist")

    verification = db.scalar(
        select(PredictionVerification).where(
            PredictionVerification.discussion_id == discussion.id
        )
    )
    if verification is not None:
        window = (
            resolve_prediction_window(discussion, calendar=calendar)
            if discussion.published_at is not None
            else None
        )
        return PredictionStatus(
            discussion=discussion,
            verification=verification,
            state="verified",
            window=window,
        )

    if discussion.status != "published" or not discussion.frozen_prediction:
        return PredictionStatus(
            discussion=discussion,
            verification=None,
            state="unavailable",
            window=None,
        )

    window = resolve_prediction_window(discussion, calendar=calendar)
    state = "eligible" if _current(moment) >= window.eligible_at else "waiting"
    return PredictionStatus(
        discussion=discussion,
        verification=None,
        state=state,
        window=window,
    )


def _parse_candle_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise PredictionMarketEvidenceError("Market candle is missing its timestamp")
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise PredictionMarketEvidenceError("Market candle timestamp is invalid") from exc
    return _aware(parsed)


def _price(candle: dict[str, object], field: str) -> float:
    value = candle.get(field)
    try:
        price = float(value)
    except (TypeError, ValueError) as exc:
        raise PredictionMarketEvidenceError(
            f"Market candle has an invalid {field} price"
        ) from exc
    if price <= 0:
        raise PredictionMarketEvidenceError(
            f"Market candle has a non-positive {field} price"
        )
    return price


def select_window_candles(
    series: CandleSeries,
    *,
    window: PredictionWindow,
    calendar: EGXTradingCalendar | None = None,
) -> tuple[dict[str, object], ...]:
    trading_calendar = calendar or EGXTradingCalendar.from_settings()
    expected_dates = set(window.session_dates)
    by_session_date: dict[date, dict[str, object]] = {}
    for raw_candle in series.candles:
        candle = dict(raw_candle)
        session_date = _parse_candle_timestamp(candle.get("timestamp")).astimezone(
            trading_calendar.timezone
        ).date()
        if session_date in expected_dates:
            by_session_date[session_date] = candle

    missing = [
        session_date.isoformat()
        for session_date in window.session_dates
        if session_date not in by_session_date
    ]
    if missing:
        raise PredictionMarketEvidenceError(
            "Final market data is incomplete for sessions: " + ", ".join(missing)
        )

    ordered = tuple(by_session_date[item] for item in window.session_dates)
    for candle in ordered:
        for field in ("open", "high", "low", "close"):
            _price(candle, field)
    return ordered


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _specificity(prediction: dict[str, Any]) -> tuple[float, bool]:
    raw_specificity = prediction.get("specificity", 0.0)
    try:
        model_specificity = _clamp(float(raw_specificity))
    except (TypeError, ValueError):
        model_specificity = 0.0

    target_price = _optional_float(prediction.get("target_price"))
    deadline = str(prediction.get("deadline") or "").strip()
    claims = prediction.get("claims")
    clean_claims = [str(item).strip() for item in claims] if isinstance(claims, list) else []
    clean_claims = [item for item in clean_claims if item]
    direction = str(prediction.get("direction") or "").strip().lower()

    structured_specificity = 0.0
    if direction in {"up", "down", "neutral"}:
        structured_specificity += 0.2
    if target_price is not None:
        structured_specificity += 0.4
    if deadline:
        structured_specificity += 0.2
    if clean_claims:
        structured_specificity += 0.2

    is_specific = target_price is not None or bool(deadline) or bool(clean_claims)
    return max(model_specificity, structured_specificity), is_specific


def calculate_prediction_score(
    *,
    prediction: dict[str, Any],
    candles: tuple[dict[str, object], ...],
    window: PredictionWindow,
    ticker: str,
) -> PredictionScore:
    if not candles:
        raise PredictionMarketEvidenceError("No market candles were supplied")

    start_price = _price(candles[0], "open")
    end_price = _price(candles[-1], "close")
    period_high = max(_price(candle, "high") for candle in candles)
    period_low = min(_price(candle, "low") for candle in candles)
    return_pct = ((end_price - start_price) / start_price) * 100.0

    if return_pct > 0.5:
        actual_direction = "up"
    elif return_pct < -0.5:
        actual_direction = "down"
    else:
        actual_direction = "neutral"

    predicted_direction = str(prediction.get("direction") or "").strip().lower()
    direction_match = predicted_direction == actual_direction
    direction_score = 4000 if direction_match else 0

    target_price = _optional_float(prediction.get("target_price"))
    target_hit = False
    target_progress = 0.0
    if target_price is not None:
        if predicted_direction == "up" and target_price > start_price:
            target_progress = _clamp(
                (period_high - start_price) / (target_price - start_price)
            )
            target_hit = period_high >= target_price
        elif predicted_direction == "down" and target_price < start_price:
            target_progress = _clamp(
                (start_price - period_low) / (start_price - target_price)
            )
            target_hit = period_low <= target_price
        elif period_low <= target_price <= period_high:
            target_progress = 1.0
            target_hit = True
        else:
            target_progress = _clamp(
                1.0 - (abs(end_price - target_price) / target_price)
            )
    target_score = round(3000 * target_progress)

    deadline_score = 1000 if direction_match else 0
    if predicted_direction == "up":
        adverse_excursion = max(0.0, (start_price - period_low) / start_price)
    elif predicted_direction == "down":
        adverse_excursion = max(0.0, (period_high - start_price) / start_price)
    else:
        adverse_excursion = max(
            abs(period_high - start_price),
            abs(start_price - period_low),
        ) / start_price

    if target_hit:
        path_score = 1000
    elif direction_match and adverse_excursion <= 0.03:
        path_score = 1000
    elif direction_match and adverse_excursion <= 0.06:
        path_score = 500
    else:
        path_score = 0
    timing_path_score = deadline_score + path_score

    specificity, is_specific = _specificity(prediction)
    specificity_score = round(1000 * specificity)

    score_bp = min(
        10000,
        direction_score + target_score + timing_path_score + specificity_score,
    )
    if score_bp < 4000:
        strength = "rejected"
        reward_points = 0
    elif score_bp < 6000:
        strength = "weak"
        reward_points = 50
    elif score_bp < 8000:
        strength = "strong"
        reward_points = 100
    elif is_specific:
        strength = "very_strong"
        reward_points = 200
    else:
        strength = "strong"
        reward_points = 100

    market_outcome = {
        "ticker": ticker.upper(),
        "start_session_date": window.start_session_date.isoformat(),
        "end_session_date": window.end_session_date.isoformat(),
        "session_count": len(window.session_dates),
        "open": round(start_price, 6),
        "high": round(period_high, 6),
        "low": round(period_low, 6),
        "close": round(end_price, 6),
        "return_percent": round(return_pct, 4),
        "actual_direction": actual_direction,
        "target_hit": target_hit,
        "target_progress": round(target_progress, 6),
        "adverse_excursion_percent": round(adverse_excursion * 100.0, 4),
    }
    evidence = {
        "algorithm_version": ALGORITHM_VERSION,
        "weights_bp": {
            "direction": 4000,
            "target": 3000,
            "timing_and_path": 2000,
            "specificity": 1000,
        },
        "components_bp": {
            "direction": direction_score,
            "target": target_score,
            "timing_and_path": timing_path_score,
            "specificity": specificity_score,
        },
        "specific_prediction": is_specific,
        "prediction": prediction,
        "market_outcome": market_outcome,
        "window": {
            "session_dates": [item.isoformat() for item in window.session_dates],
            "eligible_at": window.eligible_at.isoformat(),
        },
    }
    return PredictionScore(
        score_bp=score_bp,
        strength=strength,
        reward_points=reward_points,
        market_outcome=market_outcome,
        evidence=evidence,
    )


def deterministic_explanation(score: PredictionScore) -> str:
    components = score.evidence["components_bp"]
    direction_text = (
        "اتفق الاتجاه المتوقع مع حركة الإغلاق"
        if components["direction"] == 4000
        else "لم يتفق الاتجاه المتوقع مع حركة الإغلاق"
    )
    target_text = (
        "ووصل السعر إلى الهدف المحدد"
        if score.market_outcome["target_hit"]
        else "ولم يصل السعر إلى الهدف كاملًا"
    )
    return (
        f"{direction_text} {target_text}. "
        f"الدرجة المحسوبة بالقواعد الثابتة هي {score.score_bp / 100:.2f}%."
    )


def finalize_prediction_verification(
    db: Session,
    *,
    discussion_id: UUID,
    user_id: UUID,
    score: PredictionScore,
    explanation: dict[str, Any],
    moment: datetime | None = None,
    calendar: EGXTradingCalendar | None = None,
) -> PredictionVerificationResult:
    verified_at = _current(moment)
    discussion = db.scalar(
        select(Discussion)
        .where(
            Discussion.id == discussion_id,
            Discussion.user_id == user_id,
        )
        .with_for_update()
    )
    if discussion is None:
        raise PredictionNotFoundError("Discussion does not exist")

    existing = db.scalar(
        select(PredictionVerification)
        .where(PredictionVerification.discussion_id == discussion.id)
        .with_for_update()
    )
    if existing is not None:
        account = get_wallet_account(db, user_id)
        return PredictionVerificationResult(
            verification=existing,
            balance_points=account.balance_points,
            idempotent=True,
        )

    if discussion.status != "published" or not discussion.frozen_prediction:
        raise PredictionUnavailableError("Discussion is not eligible for verification")
    window = resolve_prediction_window(discussion, calendar=calendar)
    if verified_at < window.eligible_at:
        raise PredictionNotEligibleError(window.eligible_at)

    reward_transaction_id = f"prediction:{discussion.id}:reward"
    evidence = {
        **score.evidence,
        "explanation": explanation,
        "reward_transaction_id": reward_transaction_id
        if score.reward_points > 0
        else None,
    }
    verification = PredictionVerification(
        discussion_id=discussion.id,
        score_bp=score.score_bp,
        strength=score.strength,
        reward_points=score.reward_points,
        evidence=evidence,
        verified_at=verified_at,
    )
    db.add(verification)
    db.flush()

    if score.reward_points > 0:
        credit_points(
            db,
            user_id=user_id,
            amount_points=score.reward_points,
            transaction_id=reward_transaction_id,
            entry_type=PREDICTION_REWARD_ENTRY_TYPE,
            reference_type="prediction_verification",
            reference_id=str(verification.id),
            details={
                "discussion_id": str(discussion.id),
                "score_bp": score.score_bp,
                "strength": score.strength,
                "algorithm_version": ALGORITHM_VERSION,
            },
        )

    account = get_wallet_account(db, user_id)
    db.flush()
    return PredictionVerificationResult(
        verification=verification,
        balance_points=account.balance_points,
        idempotent=False,
    )


def get_prediction_stats(db: Session, *, user_id: UUID) -> PredictionStats:
    row = db.execute(
        select(
            func.count(PredictionVerification.id),
            func.count(PredictionVerification.id).filter(
                PredictionVerification.score_bp >= 4000
            ),
            func.coalesce(func.avg(PredictionVerification.score_bp), 0),
            func.coalesce(func.sum(PredictionVerification.reward_points), 0),
        )
        .join(
            Discussion,
            Discussion.id == PredictionVerification.discussion_id,
        )
        .where(Discussion.user_id == user_id)
    ).one()
    return PredictionStats(
        verified_predictions=int(row[0] or 0),
        accepted_predictions=int(row[1] or 0),
        average_score_bp=round(float(row[2] or 0)),
        total_reward_points=int(row[3] or 0),
    )
