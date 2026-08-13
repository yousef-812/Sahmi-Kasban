from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.market_calendar import EGXTradingCalendar
from app.market_data.types import CandleSeries
from app.models import Discussion, PredictionVerification, WalletEntry
from app.services.auth import register_user
from app.services.prediction_evaluation import (
    PredictionMarketEvidenceError,
    PredictionNotEligibleError,
    PredictionScore,
    calculate_prediction_score,
    finalize_prediction_verification,
    get_prediction_stats,
    get_prediction_status,
    resolve_prediction_window,
    select_window_candles,
)
from app.services.wallet import get_wallet_account

PASSWORD = "StrongPass123"


def calendar() -> EGXTradingCalendar:
    return EGXTradingCalendar(
        timezone_name="Africa/Cairo",
        holidays=frozenset(),
        scan_hour=15,
        scan_minute=0,
    )


def create_user(db: Session, email: str):
    user, _token = register_user(
        db,
        email=email,
        password=PASSWORD,
        display_name=email.split("@", maxsplit=1)[0],
    )
    db.commit()
    return user


def create_published_discussion(
    db: Session,
    *,
    user_id,
    period_type: str = "next_session",
    published_at: datetime = datetime(2025, 1, 2, 14, tzinfo=UTC),
    prediction: dict | None = None,
) -> Discussion:
    discussion = Discussion(
        id=uuid4(),
        user_id=user_id,
        ticker="COMI",
        title="توقع منظم لاختبار التقييم الرقمي",
        content="أتوقع حركة واضحة للسهم خلال الفترة المحددة مع هدف سعري.",
        period_type=period_type,
        status="published",
        moderation_result={"review_stage": "completed"},
        frozen_prediction=prediction
        or {
            "ticker": "COMI",
            "direction": "up",
            "target_price": 108.0,
            "deadline": "نهاية الفترة",
            "claims": ["الثبات أعلى الدعم ثم الوصول إلى الهدف"],
            "specificity": 0.9,
        },
        published_at=published_at,
    )
    db.add(discussion)
    db.flush()
    return discussion


def candle(
    timestamp: str,
    *,
    open_price: float,
    high: float,
    low: float,
    close: float,
) -> dict[str, object]:
    return {
        "timestamp": timestamp,
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": 100_000,
    }


def test_prediction_window_uses_future_cairo_sessions(db_session: Session) -> None:
    user = create_user(db_session, "window@example.com")
    discussion = create_published_discussion(
        db_session,
        user_id=user.id,
        period_type="week",
        published_at=datetime(2026, 1, 8, 12, tzinfo=UTC),
    )

    window = resolve_prediction_window(discussion, calendar=calendar())

    assert [item.isoformat() for item in window.session_dates] == [
        "2026-01-11",
        "2026-01-12",
        "2026-01-13",
        "2026-01-14",
        "2026-01-15",
    ]
    assert window.eligible_at.astimezone(calendar().timezone).isoformat() == (
        "2026-01-15T15:00:00+02:00"
    )


def test_specific_prediction_can_reach_very_strong_level(db_session: Session) -> None:
    user = create_user(db_session, "score@example.com")
    discussion = create_published_discussion(db_session, user_id=user.id)
    window = resolve_prediction_window(discussion, calendar=calendar())
    candles = (
        candle(
            "2025-01-05T00:00:00+00:00",
            open_price=100,
            high=111,
            low=99,
            close=110,
        ),
    )

    score = calculate_prediction_score(
        prediction=discussion.frozen_prediction,
        candles=candles,
        window=window,
        ticker=discussion.ticker,
    )

    assert score.score_bp == 9900
    assert score.strength == "very_strong"
    assert score.reward_points == 200
    assert score.evidence["components_bp"] == {
        "direction": 4000,
        "target": 3000,
        "timing_and_path": 2000,
        "specificity": 900,
    }


def test_generic_direction_prediction_is_capped_below_very_strong(
    db_session: Session,
) -> None:
    user = create_user(db_session, "generic@example.com")
    discussion = create_published_discussion(
        db_session,
        user_id=user.id,
        prediction={
            "ticker": "COMI",
            "direction": "up",
            "target_price": None,
            "deadline": None,
            "claims": [],
            "specificity": 0.0,
        },
    )
    window = resolve_prediction_window(discussion, calendar=calendar())

    score = calculate_prediction_score(
        prediction=discussion.frozen_prediction,
        candles=(
            candle(
                "2025-01-05T00:00:00+00:00",
                open_price=100,
                high=106,
                low=99,
                close=105,
            ),
        ),
        window=window,
        ticker=discussion.ticker,
    )

    assert score.score_bp == 6200
    assert score.strength == "strong"
    assert score.reward_points == 100
    assert score.evidence["specific_prediction"] is False


def test_missing_final_session_candle_blocks_evaluation(db_session: Session) -> None:
    user = create_user(db_session, "missing@example.com")
    discussion = create_published_discussion(
        db_session,
        user_id=user.id,
        period_type="week",
    )
    window = resolve_prediction_window(discussion, calendar=calendar())
    series = CandleSeries(
        ticker="COMI",
        provider="test",
        interval="1d",
        period="6mo",
        fetched_at=datetime.now(UTC),
        data_as_of=datetime.now(UTC),
        fingerprint="test",
        candles=(
            candle(
                f"{window.session_dates[0].isoformat()}T00:00:00+00:00",
                open_price=100,
                high=101,
                low=99,
                close=100.5,
            ),
        ),
    )

    with pytest.raises(PredictionMarketEvidenceError):
        select_window_candles(series, window=window, calendar=calendar())


def test_verification_cannot_run_before_eligible_at(db_session: Session) -> None:
    user = create_user(db_session, "early@example.com")
    discussion = create_published_discussion(
        db_session,
        user_id=user.id,
        published_at=datetime(2026, 7, 26, 1, tzinfo=UTC),
    )
    status_result = get_prediction_status(
        db_session,
        discussion_id=discussion.id,
        user_id=user.id,
        moment=datetime(2026, 7, 26, 2, tzinfo=UTC),
        calendar=calendar(),
    )
    assert status_result.state == "waiting"
    assert status_result.window is not None

    score = PredictionScore(
        score_bp=8000,
        strength="very_strong",
        reward_points=200,
        market_outcome={},
        evidence={"algorithm_version": "test"},
    )
    with pytest.raises(PredictionNotEligibleError):
        finalize_prediction_verification(
            db_session,
            discussion_id=discussion.id,
            user_id=user.id,
            score=score,
            explanation={"source": "test", "reason": "test"},
            moment=datetime(2026, 7, 26, 2, tzinfo=UTC),
            calendar=calendar(),
        )


def test_reward_and_verification_are_idempotent(db_session: Session) -> None:
    user = create_user(db_session, "reward@example.com")
    discussion = create_published_discussion(db_session, user_id=user.id)
    score = PredictionScore(
        score_bp=7500,
        strength="strong",
        reward_points=100,
        market_outcome={"actual_direction": "up"},
        evidence={"algorithm_version": "test"},
    )

    first = finalize_prediction_verification(
        db_session,
        discussion_id=discussion.id,
        user_id=user.id,
        score=score,
        explanation={"source": "test", "reason": "نجح التوقع"},
        moment=datetime(2025, 2, 1, tzinfo=UTC),
        calendar=calendar(),
    )
    repeated = finalize_prediction_verification(
        db_session,
        discussion_id=discussion.id,
        user_id=user.id,
        score=score,
        explanation={"source": "test", "reason": "لن تستخدم"},
        moment=datetime(2025, 2, 1, tzinfo=UTC),
        calendar=calendar(),
    )
    db_session.commit()

    assert first.idempotent is False
    assert repeated.idempotent is True
    assert first.verification.id == repeated.verification.id
    assert get_wallet_account(db_session, user.id).balance_points == 600
    rewards = db_session.scalars(
        select(WalletEntry).where(
            WalletEntry.entry_type == "prediction_verification_reward"
        )
    ).all()
    assert len(rewards) == 1
    assert rewards[0].amount_points == 100
    assert db_session.scalar(
        select(PredictionVerification).where(
            PredictionVerification.discussion_id == discussion.id
        )
    ) is not None

    stats = get_prediction_stats(db_session, user_id=user.id)
    assert stats.verified_predictions == 1
    assert stats.accepted_predictions == 1
    assert stats.average_score_bp == 7500
    assert stats.total_reward_points == 100
