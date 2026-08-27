from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "backtest_2025"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    symbols: set[str] = set()

    seed_path = ROOT / "backend" / "app" / "market_data" / "egx_symbols.py"
    sys.path.insert(0, str(ROOT / "backend"))
    from app.market_data.egx_symbols import EGX_SEED_SYMBOLS  # type: ignore[import-not-found]

    symbols.update(EGX_SEED_SYMBOLS)

    for csv_path in (ROOT / "sahmi-engine").glob("sahmi-engine-replay-2025-*.csv"):
        frame = pd.read_csv(csv_path, usecols=["ticker"])
        symbols.update(str(t).strip().upper() for t in frame["ticker"].dropna())

    symbols = {s for s in symbols if s}
    ordered = sorted(symbols)
    (OUT_DIR / "universe.json").write_text(
        json.dumps({"count": len(ordered), "symbols": ordered}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Universe: {len(ordered)} symbols -> {OUT_DIR / 'universe.json'}")


if __name__ == "__main__":
    main()
