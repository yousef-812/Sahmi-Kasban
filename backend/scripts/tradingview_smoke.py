from __future__ import annotations

import asyncio
import json

from app.market_data.tradingview import TradingViewMarketDataProvider


async def main() -> None:
    provider = TradingViewMarketDataProvider()
    series = await provider.get_history(
        "COMI",
        period="1y",
        interval="1d",
    )
    if series.candle_count < 200:
        raise RuntimeError(
            f"TradingView returned only {series.candle_count} candles for COMI"
        )
    last_candle = series.candles[-1]
    close_price = float(last_candle["close"])
    if close_price <= 0:
        raise RuntimeError("TradingView returned a non-positive COMI close")
    print(
        json.dumps(
            {
                "status": "ok",
                "provider": series.provider,
                "ticker": series.ticker,
                "candle_count": series.candle_count,
                "data_as_of": series.data_as_of.isoformat(),
                "last_close": close_price,
                "last_volume": float(last_candle["volume"]),
                "fingerprint_prefix": series.fingerprint[:12],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
