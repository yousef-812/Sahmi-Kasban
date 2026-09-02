from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import AnalysisReplayTicker, MarketInstrumentCatalog

_ISIN_LIKE_PATTERN = re.compile(r"^EGS[A-Z0-9]{9,}$")
_PROVIDER_FAILURE_CODES = frozenset({"MarketDataUnavailableError"})
DEFAULT_FAILURE_QUARANTINE_THRESHOLD = 3


@dataclass(frozen=True, slots=True)
class TradableUniverse:
    tickers: tuple[str, ...]
    active_catalog_count: int
    incompatible_symbol_count: int
    replay_failure_quarantine_count: int


def is_provider_compatible_ticker(ticker: str) -> bool:
    normalized = ticker.strip().upper()
    if not normalized or _ISIN_LIKE_PATTERN.fullmatch(normalized):
        return False
    return normalized.isalnum() and len(normalized) <= 12


def _replay_failure_quarantine(
    db: Session,
    *,
    min_failures: int,
) -> set[str]:
    failure_count = func.sum(
        case(
            (
                (AnalysisReplayTicker.status == "failed")
                & AnalysisReplayTicker.error_code.in_(_PROVIDER_FAILURE_CODES),
                1,
            ),
            else_=0,
        )
    )
    evaluated_success_count = func.sum(case((AnalysisReplayTicker.evaluated_rows > 0, 1), else_=0))
    rows = db.execute(
        select(
            AnalysisReplayTicker.ticker,
            failure_count.label("failure_count"),
            evaluated_success_count.label("evaluated_success_count"),
        )
        .group_by(AnalysisReplayTicker.ticker)
        .having(failure_count >= min_failures)
        .having(evaluated_success_count == 0)
    ).all()
    return {str(row.ticker).upper() for row in rows}


def tradable_market_universe(
    db: Session,
    *,
    min_failures: int = DEFAULT_FAILURE_QUARANTINE_THRESHOLD,
) -> TradableUniverse:
    active = tuple(
        db.scalars(
            select(MarketInstrumentCatalog.ticker)
            .where(MarketInstrumentCatalog.active.is_(True))
            .order_by(MarketInstrumentCatalog.ticker.asc())
        ).all()
    )
    compatible = tuple(ticker for ticker in active if is_provider_compatible_ticker(ticker))
    quarantined = _replay_failure_quarantine(db, min_failures=min_failures)
    tickers = tuple(ticker for ticker in compatible if ticker not in quarantined)
    return TradableUniverse(
        tickers=tickers,
        active_catalog_count=len(active),
        incompatible_symbol_count=len(active) - len(compatible),
        replay_failure_quarantine_count=len(set(compatible).intersection(quarantined)),
    )


def apply_market_health_quarantine(
    db: Session,
    *,
    min_failures: int = DEFAULT_FAILURE_QUARANTINE_THRESHOLD,
) -> TradableUniverse:
    """Deactivate symbols proven unusable without reacting to one transient failure.

    Scanner refreshes may reactivate symbols because they are still listed. The replay
    worker calls this immediately after a refresh, so only ISIN-like aliases or symbols
    with at least three provider failures and no evaluated replay are removed.
    """

    universe = tradable_market_universe(db, min_failures=min_failures)
    allowed = set(universe.tickers)
    active_rows = db.scalars(
        select(MarketInstrumentCatalog).where(MarketInstrumentCatalog.active.is_(True))
    ).all()
    changed = False
    for row in active_rows:
        if row.ticker not in allowed:
            row.active = False
            changed = True
    if changed:
        db.commit()
    return universe
