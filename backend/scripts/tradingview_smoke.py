from __future__ import annotations

import asyncio
import json

from reusable_data_fetcher import StockDataFetcher


async def main() -> None:
    fetcher = StockDataFetcher(tv_token="unauthorized_user_token")
    try:
        data = await fetcher.get_full_data("COMI", market="EGX")
    finally:
        await fetcher.close()

    historical = data["historical"]
    indicators = data["indicators"]
    price = data["price"]
    fundamentals = data["fundamentals"]

    if len(historical) < 200:
        raise RuntimeError(
            f"TradingView returned only {len(historical)} COMI candles"
        )
    last_close = float(historical[-1]["close"])
    if last_close <= 0:
        raise RuntimeError("TradingView returned a non-positive COMI close")
    if indicators.get("rsi") is None:
        raise RuntimeError("Technical indicators were not calculated")

    print(
        json.dumps(
            {
                "status": "ok",
                "symbol": data["symbol"],
                "market": data["market"],
                "price": price.get("price"),
                "price_source": price.get("source"),
                "candle_count": len(historical),
                "last_timestamp": historical[-1]["timestamp"],
                "last_close": last_close,
                "last_volume": float(historical[-1]["volume"]),
                "rsi": indicators.get("rsi"),
                "macd": indicators.get("macd"),
                "trend": indicators.get("trend"),
                "company_name": fundamentals.get("company_name"),
                "market_cap": fundamentals.get("market_cap"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
