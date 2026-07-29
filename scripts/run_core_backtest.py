from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from sahmi_kasban import walk_forward_backtest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a no-lookahead walk-forward backtest for Sahmi Kasban Core V2."
    )
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--min-train-size", type=int, default=200)
    parser.add_argument("--horizon-sessions", type=int, default=5)
    parser.add_argument("--step-sessions", type=int, default=5)
    parser.add_argument("--neutral-band-pct", type=float, default=1.0)
    parser.add_argument("--summary-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candles = pd.read_csv(args.csv_path)
    summary = walk_forward_backtest(
        args.ticker,
        candles,
        min_train_size=args.min_train_size,
        horizon_sessions=args.horizon_sessions,
        step_sessions=args.step_sessions,
        neutral_band_pct=args.neutral_band_pct,
    )
    print(
        json.dumps(
            summary.to_dict(include_results=not args.summary_only),
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
