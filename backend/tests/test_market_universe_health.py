from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.market_data.universe import (
    apply_market_health_quarantine,
    is_provider_compatible_ticker,
    tradable_market_universe,
)
from app.models import (
    AnalysisReplayJob,
    AnalysisReplayTicker,
    MarketInstrumentCatalog,
    User,
)


def _job(user: User, index: int) -> AnalysisReplayJob:
    return AnalysisReplayJob(
        request_key=f"health-{index}",
        requested_by=user.id,
        engine_version="core-v2.2",
        status="complete",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        horizon_sessions=5,
        min_train_size=200,
        neutral_band_bp=100,
        parallelism=5,
        total_tickers=1,
        processed_tickers=1,
        successful_tickers=0,
        failed_tickers=1,
        total_rows=0,
        evaluated_rows=0,
        pending_rows=0,
        details={},
    )


def _task(job: AnalysisReplayJob, ticker: str, *, success: bool = False) -> AnalysisReplayTicker:
    return AnalysisReplayTicker(
        job_id=job.id,
        ticker=ticker,
        status="complete" if success else "failed",
        candle_count=260 if success else 0,
        rows_written=20 if success else 0,
        evaluated_rows=20 if success else 0,
        pending_rows=0,
        failed_rows=0,
        error_code=None if success else "MarketDataUnavailableError",
        error_message=None if success else "provider history unavailable",
        completed_at=datetime.now(UTC),
    )


def test_provider_compatibility_rejects_isin_aliases() -> None:
    assert is_provider_compatible_ticker("COMI") is True
    assert is_provider_compatible_ticker("EGS60121C018") is False
    assert is_provider_compatible_ticker("BAD-SYMBOL") is False


def test_universe_quarantines_repeated_failures_but_keeps_recovered_symbols(
    db_session: Session,
) -> None:
    user = User(
        email="health@example.com",
        password_hash="hash",
        display_name="Health Test",
        email_verified=True,
    )
    db_session.add(user)
    db_session.flush()
    now = datetime.now(UTC)
    for ticker in ("COMI", "DEAD", "RECOVER", "EGS60121C018"):
        db_session.add(
            MarketInstrumentCatalog(
                ticker=ticker,
                provider_symbol=f"EGX:{ticker}",
                exchange="EGX",
                description=ticker,
                source="tradingview_scanner",
                active=True,
                last_seen_at=now,
            )
        )

    for index in range(3):
        job = _job(user, index)
        db_session.add(job)
        db_session.flush()
        db_session.add_all(
            [
                _task(job, "DEAD"),
                _task(job, "RECOVER"),
            ]
        )
    recovered_job = _job(user, 99)
    db_session.add(recovered_job)
    db_session.flush()
    db_session.add(_task(recovered_job, "RECOVER", success=True))
    db_session.commit()

    universe = tradable_market_universe(db_session)

    assert universe.tickers == ("COMI", "RECOVER")
    assert universe.incompatible_symbol_count == 1
    assert universe.replay_failure_quarantine_count == 1

    apply_market_health_quarantine(db_session)
    rows = {row.ticker: row for row in db_session.query(MarketInstrumentCatalog).all()}
    assert rows["COMI"].active is True
    assert rows["RECOVER"].active is True
    assert rows["DEAD"].active is False
    assert rows["EGS60121C018"].active is False
