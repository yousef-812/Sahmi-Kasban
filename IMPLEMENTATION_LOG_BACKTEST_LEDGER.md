# Persistent backtest performance ledger

- Branch: `agent/backtest-performance-ledger`
- Base: deployed `main` commit `12eaeaa58db90b60dd8e5e68526f4ef0c293a29d`.
- Added PostgreSQL runs, ticker results, and per-cutoff observation tables.
- Added bounded administrator execution for one to three EGX tickers.
- Added idempotency signatures so identical requests do not repeat provider work.
- Retained provider failures, negative returns, WATCH observations, and losing BUY outcomes.
- Added engine-version aggregation for comparing Core V2 with future engine namespaces.
- Added service, API, migration, PostgreSQL, and Alembic regression coverage.
