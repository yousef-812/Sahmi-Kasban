"""Manual live-data smoke test for the configured TradingView adapter.

Run only when written authorization covers automated collection and algorithmic
processing for this application. This test intentionally fails closed otherwise.
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.providers.tradingview import TradingViewWebSocketProvider  # noqa: E402
from app.providers.base import MarketDataError  # noqa: E402


def main() -> int:
    symbol = os.getenv("SMOKE_TEST_SYMBOL", "COMI").strip().upper()
    if not symbol:
        print("ERROR: SMOKE_TEST_SYMBOL must not be empty.", file=sys.stderr)
        return 2

    if os.getenv("TRADINGVIEW_DATA_USAGE_AUTHORIZED", "").strip().lower() != "true":
        print(
            "ERROR: live test blocked. Configure the repository secret "
            "TRADINGVIEW_DATA_USAGE_AUTHORIZED=true only after obtaining written "
            "permission covering automated collection and algorithmic analysis.",
            file=sys.stderr,
        )
        return 2

    if not os.getenv("TRADINGVIEW_AUTH_TOKEN"):
        print(
            "ERROR: repository secret TRADINGVIEW_AUTH_TOKEN is missing.",
            file=sys.stderr,
        )
        return 2

    try:
        candles = TradingViewWebSocketProvider().daily_candles(symbol)
    except (MarketDataError, ValueError, OSError) as exc:
        print(f"ERROR: live data fetch failed for {symbol}: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # Keep the workflow failure informative without secrets.
        print(
            f"ERROR: unexpected provider failure ({type(exc).__name__}); "
            "inspect the provider implementation and runner logs.",
            file=sys.stderr,
        )
        return 1

    required = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = required.difference(candles.columns)
    if missing:
        print(f"ERROR: missing required columns: {sorted(missing)}", file=sys.stderr)
        return 1
    if len(candles) < 60:
        print(f"ERROR: only {len(candles)} usable candles returned; need at least 60.", file=sys.stderr)
        return 1

    numeric = candles[["open", "high", "low", "close", "volume"]]
    if numeric.isna().any().any() or not numeric.apply(lambda col: col.map(pd.notna).all()).all():
        print("ERROR: OHLCV contains null or non-numeric values.", file=sys.stderr)
        return 1
    if (candles["high"] < candles[["open", "close", "low"]].max(axis=1)).any():
        print("ERROR: invalid candle data: high is below open/close/low.", file=sys.stderr)
        return 1
    if (candles["low"] > candles[["open", "close", "high"]].min(axis=1)).any():
        print("ERROR: invalid candle data: low is above open/close/high.", file=sys.stderr)
        return 1

    latest = pd.to_datetime(candles["timestamp"], utc=True, errors="coerce").max()
    if pd.isna(latest):
        print("ERROR: no valid candle timestamps returned.", file=sys.stderr)
        return 1

    age_days = (datetime.now(timezone.utc) - latest.to_pydatetime()).total_seconds() / 86400
    print(f"PASS: provider returned {len(candles)} usable daily candles for {symbol}.")
    print(f"Latest candle timestamp (UTC): {latest.isoformat()}")
    print(f"Latest candle age: {age_days:.2f} days.")
    if age_days > 10:
        print("WARNING: latest candle is older than 10 days; verify ticker mapping and market calendar.")
    print("PASS: required OHLCV fields and candle high/low consistency checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
