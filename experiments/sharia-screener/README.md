# Sharia Screener (MVP)

Arabic-first daily technical screening for EGX Sharia-compliant stocks. This is an isolated prototype in the `sharia-screener-mvp` branch; it does not change the existing Sahmi Kasban app.

## Features
- FastAPI server with health, single-stock analysis and all-universe scan endpoints.
- Daily OHLCV indicator engine: MACD (12,26,9), Stoch RSI (3,3,14,14), RSI(14), MFI(14), DMI/ADX(14), and a configurable custom indicator slot for the screenshot's "33".
- Deterministic, explainable scoring and entry/stop/target levels based on ATR.
- Data-provider interface. Use a licensed EGX data vendor or a permitted source. TradingView's published terms prohibit automated extraction and non-display use of its market data; do not scrape its site or use unofficial private endpoints.
- Sharia universe is a maintained input list, not inferred from chart data. Verify eligibility against the official index constituent list/current Sharia screening source before every run.

## Run backend
```bash
cd experiments/sharia-screener/backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

Set `DATA_PROVIDER=csv` for local demo data. The experiment now reuses the repository's existing `backend/reusable_data_fetcher.py` WebSocket connector through `app/providers/tradingview.py`.

To select it, set `DATA_PROVIDER=tradingview`. It is intentionally blocked unless `TRADINGVIEW_DATA_USAGE_AUTHORIZED=true` is explicitly set. Only enable that flag if written permission covers automated collection and algorithmic processing for this application. TradingView's published terms restrict automated data extraction and non-display algorithmic use; for an unlicensed use case, keep CSV mode or connect a licensed provider. The adapter does not bypass login, rate limits, or access controls.

The TradingView adapter requests daily OHLCV candles using the existing `TradingViewConnector.get_historical()` method, normalizes the returned records, and passes them to the same indicator engine. No fabricated live quotes are returned; absent or invalid data produces a clear provider error.

## CSV format
Put daily candles in `backend/data/{SYMBOL}.csv` with columns:
`timestamp,open,high,low,close,volume`.
Symbols listed in `backend/data/sharia_universe.txt`, one per line.

## API
- `GET /health`
- `GET /api/v1/universe`
- `POST /api/v1/scan` — analyze all configured symbols
- `GET /api/v1/analysis/{symbol}` — analyze one symbol

## Strategy (research baseline, not a guaranteed signal)
- First gate: stock must exist in the verified Sharia universe and have sufficient data/liquidity.
- Long bias requires close above EMA20 and EMA50, positive MACD histogram or improving MACD, and DMI +DI above -DI.
- Pullback timing uses Stoch RSI crossing upward from a low zone; RSI/MFI filter weak momentum and extreme conditions.
- Composite score 0–100; candidates are ranked, not auto-traded. No BUY is emitted when inputs are stale/missing.
- Entry zone is based on close/ATR; stop and targets are ATR-derived. Validate via walk-forward backtests including fees, slippage, limit moves, and survivorship bias before real money.

## Indicator "33"
The screenshot appears to label a custom indicator as "مؤشر القوة الحقيقية 13 13 25" and the user says "مؤشر 33". Its exact formula/source is not legible/defined. The MVP exposes a clearly labelled placeholder slot; do not pretend it reproduces the proprietary indicator. Supply its Pine Script/formula or exact name to implement it accurately.

## Mobile client
The `mobile/` folder contains setup notes and a minimal Flutter API client starter. Configure `API_BASE_URL` for the deployed server.
