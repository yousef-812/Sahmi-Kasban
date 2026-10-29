# Flutter mobile client

Use the existing Sahmi Kasban Flutter conventions rather than duplicating auth or secrets.

## MVP screens
1. Daily ranked list: score, signal, close, timestamp, reasons.
2. Single stock: indicators, entry zone, stop and targets.
3. Universe status: number of verified Sharia symbols and data freshness.
4. Provider status/error state.

## API wiring
- Base URL: compile-time `API_BASE_URL`; never hardcode a private host.
- `GET /api/v1/universe`
- `POST /api/v1/scan`
- `GET /api/v1/analysis/{symbol}`

The backend currently uses CSV demo input and intentionally does not invent live data. For production, connect a licensed EGX OHLCV provider, add auth/rate limits, persistence, job scheduling, and audit logging. Run scan after official daily closing data is final, not simply at a fixed time if the feed is delayed.
