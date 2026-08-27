from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from sahmi_kasban.indicators import enrich_indicators, prepare_candles

ROOT = Path(__file__).resolve().parents[2]
CANDLE_DIR = ROOT / "backtest_2025" / "data" / "candles"
PREPARED_DIR = ROOT / "backtest_2025" / "data" / "prepared"
PREPARED_DIR.mkdir(parents=True, exist_ok=True)

MIN_HISTORY = 200


def main() -> None:
    universe = json.loads((ROOT / "backtest_2025" / "universe.json").read_text(encoding="utf-8"))
    tickers = [
        s for s in universe["symbols"] if (CANDLE_DIR / f"{s}.parquet").exists()
    ]
    print(f"Preparing {len(tickers)} tickers")

    calendar: set[date] = set()
    for index, ticker in enumerate(tickers, start=1):
        out_path = PREPARED_DIR / f"{ticker}.parquet"
        if out_path.exists():
            frame = pd.read_parquet(out_path)
            if not frame.empty:
                calendar.update(pd.to_datetime(frame["timestamp"], utc=True).dt.date)
                if index % 50 == 0:
                    print(f"[{index}/{len(tickers)}] cached {ticker}")
                continue
        frame = pd.read_parquet(CANDLE_DIR / f"{ticker}.parquet")
        if "timestamp" in frame.columns:
            frame["timestamp"] = pd.to_datetime(
                frame["timestamp"], unit="s", errors="coerce", utc=True
            )
        try:
            prepared = enrich_indicators(prepare_candles(frame))
        except Exception as exc:
            print(f"[{index}/{len(tickers)}] {ticker} prepare FAILED: {exc}")
            continue
        prepared.to_parquet(out_path, index=False)
        calendar.update(pd.to_datetime(prepared["timestamp"], utc=True).dt.date)
        if index % 50 == 0:
            print(f"[{index}/{len(tickers)}] {ticker} ok rows={len(prepared)}")

    year_2025 = sorted(d for d in calendar if date(2025, 1, 1) <= d <= date(2025, 12, 31))
    print(f"Prepared done. 2025 calendar days: {len(year_2025)}")
    (ROOT / "backtest_2025" / "sessions_2025.json").write_text(
        json.dumps(
            {"count": len(year_2025), "dates": [d.isoformat() for d in year_2025]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
