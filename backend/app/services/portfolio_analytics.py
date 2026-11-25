"""Portfolio analytics over the user's open trade signals.

The repo has no brokerage/holdings integration, so the realistic portfolio is
the set of the user's own open ``Signal`` rows (states that still allow a
transition per ``signal_lifecycle.state_transitions()``). The user's watchlist
acts as an exposure hint and as a last-price fallback. Correlation is Pearson
on aligned daily close returns fetched through the shared market-data snapshot
cache (``get_cached_or_fresh_history``), so nothing here hits the network
directly and every number is deterministic given the stored rows and candles.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.market_data.cache import get_cached_or_fresh_history
from app.market_data.provider import get_market_data_provider
from app.market_data.quotes import _resolve_canonical_sector
from app.market_data.types import CandleSeries, MarketDataProvider
from app.models import Signal, WatchlistItem
from app.services.signal_lifecycle import state_transitions

ANALYTICS_VERSION = "portfolio-analytics-v1"
CORRELATION_LOOKBACK_SESSIONS = 60
MIN_CORRELATION_OBSERVATIONS = 5
CONCENTRATION_THRESHOLD = 0.4
UNKNOWN_SECTOR = "unknown"
LOW_POSITION_COUNT = 2


def open_signal_states() -> frozenset[str]:
    """Return the non-terminal signal states that still count as open positions."""
    return frozenset(state for state, targets in state_transitions().items() if targets)


def _finite(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _close_returns(series: CandleSeries, *, lookback: int) -> dict[str, float]:
    """Map candle timestamp -> close-to-close return for the last ``lookback`` sessions."""
    closes: list[tuple[str, float]] = []
    for candle in series.candles:
        timestamp = candle.get("timestamp")
        close = _finite(candle.get("close"))
        if timestamp is None or close is None:
            continue
        closes.append((str(timestamp), close))
    returns: dict[str, float] = {}
    for index in range(1, len(closes)):
        previous_close = closes[index - 1][1]
        if previous_close <= 0:
            continue
        timestamp, close = closes[index]
        returns[timestamp] = close / previous_close - 1.0
    items = list(returns.items())
    return dict(items[-lookback:])


def _pearson(left: list[float], right: list[float]) -> float | None:
    """Pearson coefficient of two aligned series; ``None`` when undefined."""
    count = len(left)
    if count < 2 or count != len(right):
        return None
    mean_left = sum(left) / count
    mean_right = sum(right) / count
    covariance = sum(
        (left_value - mean_left) * (right_value - mean_right)
        for left_value, right_value in zip(left, right, strict=True)
    )
    variance_left = sum((value - mean_left) ** 2 for value in left)
    variance_right = sum((value - mean_right) ** 2 for value in right)
    if variance_left <= 0.0 or variance_right <= 0.0:
        return None
    return covariance / (variance_left * variance_right) ** 0.5


def _correlation_block(
    returns_by_ticker: dict[str, dict[str, float]],
    *,
    lookback: int,
    min_observations: int,
) -> tuple[dict[str, object], list[str]]:
    """Build a symmetric pairwise matrix; insufficient series are omitted with a warning."""
    warnings: list[str] = []
    eligible: dict[str, dict[str, float]] = {}
    for ticker, series_returns in returns_by_ticker.items():
        if len(series_returns) >= min_observations:
            eligible[ticker] = series_returns
        else:
            warnings.append(
                f"Insufficient return history for {ticker} "
                f"({len(series_returns)} < {min_observations} observations); "
                "excluded from the correlation matrix."
            )
    tickers = sorted(eligible)
    matrix: dict[str, dict[str, float | None]] = {ticker: {} for ticker in tickers}
    for index, left in enumerate(tickers):
        matrix[left][left] = 1.0
        for right in tickers[index + 1 :]:
            common = sorted(set(eligible[left]) & set(eligible[right]))
            if len(common) < min_observations:
                matrix[left][right] = None
                matrix[right][left] = None
                warnings.append(
                    f"Insufficient overlapping history for {left}/{right}; "
                    "their correlation is unavailable."
                )
                continue
            value = _pearson(
                [eligible[left][timestamp] for timestamp in common],
                [eligible[right][timestamp] for timestamp in common],
            )
            rounded = None if value is None else round(value, 4)
            matrix[left][right] = rounded
            matrix[right][left] = rounded
    block = {
        "lookback_sessions": lookback,
        "min_observations": min_observations,
        "tickers": tickers,
        "matrix": matrix,
    }
    return block, warnings


def portfolio_warnings(
    positions: list[dict],
    *,
    concentration_threshold: float = CONCENTRATION_THRESHOLD,
) -> list[str]:
    """Return the human-readable risk notes for the computed portfolio."""
    if not positions:
        return ["No open positions; portfolio analytics are empty."]
    warnings: list[str] = []
    count = len(positions)
    if count <= LOW_POSITION_COUNT:
        warnings.append(
            f"Portfolio holds only {count} open position(s); "
            "diversification metrics are not meaningful."
        )
    for position in positions:
        if position["current_price"] is None:
            warnings.append(
                f"No recent price available for {position['ticker']}; unrealized PnL is unknown."
            )
        weight = float(position["weight"])
        if weight > concentration_threshold:
            warnings.append(
                f"{position['ticker']} represents {weight:.0%} of open exposure, "
                f"above the {concentration_threshold:.0%} single-name concentration threshold."
            )
    if count >= 2:
        sectors = {(position["sector"] or UNKNOWN_SECTOR) for position in positions}
        if len(sectors) == 1:
            warnings.append(
                f"All {count} open positions are in the {next(iter(sectors))} sector; "
                "sector diversification is zero."
            )
    return warnings


async def compute_portfolio_analytics(db: Session, user_id: UUID) -> dict:
    """Compute correlation, diversification and sector exposure for a user's open signals.

    Weights use ``abs(entry)`` as the position-sizing basis (there are no share
    quantities): ``weight_i = abs(entry_i) / sum(abs(entry_j))``. The analytics
    are computed live on every request; only the underlying candles go through
    the shared market-data cache (``market_data_cache_minutes`` TTL).
    """
    moment = datetime.now(UTC)
    signals = list(
        db.scalars(
            select(Signal)
            .where(
                Signal.user_id == user_id,
                Signal.state.in_(open_signal_states()),
            )
            .order_by(Signal.opened_at, Signal.ticker)
        ).all()
    )
    watchlist_items = list(
        db.scalars(
            select(WatchlistItem)
            .where(WatchlistItem.user_id == user_id)
            .order_by(WatchlistItem.ticker)
        ).all()
    )
    watchlist_prices = {
        item.ticker: price
        for item in watchlist_items
        if (price := _finite(item.last_price)) is not None
    }

    unique_tickers = sorted({signal.ticker for signal in signals})
    history: dict[str, CandleSeries] = {}
    if unique_tickers:
        provider: MarketDataProvider = get_market_data_provider()
        for ticker in unique_tickers:
            try:
                series, _cached = await get_cached_or_fresh_history(db, provider, ticker)
            except Exception:
                db.rollback()
                continue
            history[ticker] = series

    total_exposure = sum(abs(float(signal.entry)) for signal in signals)
    raw_weights = [
        abs(float(signal.entry)) / total_exposure if total_exposure > 0 else 0.0
        for signal in signals
    ]
    positions: list[dict] = []
    for signal, weight in zip(signals, raw_weights, strict=True):
        entry = float(signal.entry)
        series = history.get(signal.ticker)
        current_price = None
        if series is not None and series.candles:
            current_price = _finite(series.candles[-1].get("close"))
        if current_price is None:
            current_price = watchlist_prices.get(signal.ticker)
        unrealized_pct = None
        if current_price is not None and entry > 0:
            if signal.direction == "short":
                unrealized_pct = (entry - current_price) / entry * 100.0
            else:
                unrealized_pct = (current_price - entry) / entry * 100.0
        positions.append(
            {
                "ticker": signal.ticker,
                "direction": signal.direction,
                "entry": entry,
                "stop": float(signal.stop),
                "current_price": current_price,
                "weight": round(weight, 6),
                "sector": _resolve_canonical_sector(signal.ticker, None),
                "unrealized_pct": None if unrealized_pct is None else round(unrealized_pct, 4),
            }
        )

    herfindahl = sum(weight * weight for weight in raw_weights)
    effective_positions = (1.0 / herfindahl) if herfindahl > 0 else 0.0
    diversification = {
        "herfindahl": round(herfindahl, 6),
        "effective_positions": round(effective_positions, 4),
        "concentration_flag": any(weight > CONCENTRATION_THRESHOLD for weight in raw_weights),
        "concentration_threshold": CONCENTRATION_THRESHOLD,
    }

    sector_weights: dict[str, float] = {}
    for signal, weight in zip(signals, raw_weights, strict=True):
        sector = _resolve_canonical_sector(signal.ticker, None) or UNKNOWN_SECTOR
        sector_weights[sector] = sector_weights.get(sector, 0.0) + weight
    sector_exposure = {
        sector: round(weight, 6) for sector, weight in sorted(sector_weights.items())
    }

    correlation, correlation_warnings = _correlation_block(
        {
            ticker: _close_returns(series, lookback=CORRELATION_LOOKBACK_SESSIONS)
            for ticker, series in history.items()
        },
        lookback=CORRELATION_LOOKBACK_SESSIONS,
        min_observations=MIN_CORRELATION_OBSERVATIONS,
    )
    warnings = portfolio_warnings(positions)
    warnings.extend(correlation_warnings)
    for ticker in unique_tickers:
        if ticker not in history:
            warnings.append(
                f"No candle history available for {ticker}; excluded from the correlation matrix."
            )

    return {
        "as_of": moment,
        "position_count": len(positions),
        "positions": positions,
        "correlation": correlation,
        "diversification": diversification,
        "sector_exposure": sector_exposure,
        "watchlist": {
            "count": len(watchlist_items),
            "tickers": [item.ticker for item in watchlist_items],
        },
        "warnings": warnings,
        "analytics_version": ANALYTICS_VERSION,
    }
