# Persistent Core backtesting

This layer turns Core V2 walk-forward validation into an auditable PostgreSQL ledger.

## Stored entities

- `analysis_backtest_runs` records the exact engine version, ticker set, data period,
  walk-forward parameters, administrator, status, and idempotency signature.
- `analysis_backtest_results` stores one complete or failed result per ticker. Failed and
  negative outcomes remain visible and are never filtered out.
- `analysis_backtest_observations` stores every frozen cutoff, signal, score, confidence,
  entry, exit, forward return, upside, drawdown, and correctness result.

Percentage metrics are stored as integer basis points. Profit factor is stored in thousandths.
Raw market-data fingerprints and `data_as_of` values make each run traceable to the provider
response used for the calculation.

## Administrator API

Create a bounded run:

```http
POST /api/v1/admin/operations/backtests/runs
```

```json
{
  "request_key": "corev2-comi-5y-001",
  "tickers": ["COMI"],
  "period": "5y",
  "interval": "1d",
  "min_train_size": 200,
  "horizon_sessions": 5,
  "step_sessions": 20,
  "neutral_band_pct": 1.0
}
```

A request accepts at most three tickers to protect the Fly web machine and the market-data
provider. Reusing the same request key with the same parameters returns the stored run without
calling the provider again. Reusing it with different parameters returns HTTP 409.

Available reads:

- `GET /api/v1/admin/operations/backtests/runs`
- `GET /api/v1/admin/operations/backtests/runs/{run_id}`
- `GET /api/v1/admin/operations/backtests/versions`

The versions endpoint aggregates completed ticker results by engine namespace. This provides a
stable comparison surface for `core-v2` and future engine releases without rewriting historical
records.

## Interpretation

Backtest measurements describe historical behavior only. They are not profit promises and must
not be used to hide losing observations or to tune an engine on future candles.
