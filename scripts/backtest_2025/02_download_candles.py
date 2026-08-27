from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from reusable_data_fetcher import StockDataFetcher  # type: ignore[import-not-found]

DATA_DIR = ROOT / "backtest_2025" / "data" / "candles"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CANDLE_COUNT = 900


def main() -> None:
    universe = json.loads((ROOT / "backtest_2025" / "universe.json").read_text(encoding="utf-8"))
    symbols = universe["symbols"]
    missing = [s for s in symbols if not (DATA_DIR / f"{s}.parquet").exists()]
    print(f"Symbols total={len(symbols)} missing={len(missing)}")

    async def run() -> None:
        fetcher = StockDataFetcher(pool_size=2, timeout_seconds=30)
        try:
            ok = failed = 0
            for index, symbol in enumerate(missing, start=1):
                out_path = DATA_DIR / f"{symbol}.parquet"
                try:
                    candles = await fetcher.get_historical_data(
                        symbol, "EGX", "1D", CANDLE_COUNT
                    )
                except Exception as exc:
                    print(f"[{index}/{len(missing)}] {symbol} ERROR {type(exc).__name__}: {exc}")
                    failed += 1
                    continue
                if not candles:
                    print(f"[{index}/{len(missing)}] {symbol} no data")
                    failed += 1
                    continue
                frame = pd.DataFrame(candles)
                frame.to_parquet(out_path, index=False)
                ok += 1
                if index % 10 == 0 or index == len(missing):
                    print(f"[{index}/{len(missing)}] ok={ok} failed={failed}")
            print(f"DONE ok={ok} failed={failed}")
        finally:
            await fetcher.close()

    asyncio.run(run())


if __name__ == "__main__":
    main()
