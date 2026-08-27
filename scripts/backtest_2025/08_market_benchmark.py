from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PREPARED_DIR = Path("/tmp/bt_output/prepared")


def load_all() -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for path in PREPARED_DIR.glob("*.pkl"):
        df = pd.read_pickle(path)
        if df.empty:
            continue
        df = df.sort_values("timestamp").reset_index(drop=True)
        frames[path.stem] = df
    return frames


def year_return(df: pd.DataFrame, year: int) -> float | None:
    dates = pd.to_datetime(df["timestamp"], utc=True)
    closes = df["close"].to_numpy(dtype=float)
    mask = np.array(dates.dt.year == year)
    idx = np.flatnonzero(mask)
    if len(idx) < 2:
        return None
    first, last = closes[idx[0]], closes[idx[-1]]
    if not np.isfinite(first) or not np.isfinite(last) or first <= 0:
        return None
    return float(last / first - 1.0)


def benchmark(year: int, frames: dict[str, pd.DataFrame]) -> dict:
    per_ticker: list[float] = []
    for ticker, df in frames.items():
        ret = year_return(df, year)
        if ret is not None:
            per_ticker.append(ret)
    arr = np.array(per_ticker)
    market = float(np.mean(arr) * 100)
    winners = int((arr > 0).sum())
    return {
        "year": year,
        "market": f"{market:+.2f}%",
        "sessions": len(frames),
        "winners": winners,
        "median": f"{np.median(arr) * 100:+.1f}%",
    }


def main() -> None:
    years = [int(a) for a in sys.argv[1:]] or [2022, 2023, 2024, 2025]
    frames = load_all()
    print(f"[bm] loaded {len(frames)} tickers", flush=True)
    results = {}
    for year in years:
        res = benchmark(year, frames)
        print(f"[bm] {year}: {res}", flush=True)
        results[str(year)] = res
    out = Path("/tmp/bt_output/market_benchmark.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[bm] saved {out}", flush=True)


if __name__ == "__main__":
    main()
