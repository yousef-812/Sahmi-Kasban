# Core V2 implementation log

- Branch: `agent/core-v2-backtesting`
- Engine namespace: `core-v2`
- Added confidence-aware weighted aggregation and disagreement penalties.
- Added BUY confirmation gates for directional consensus, risk, and confidence.
- Calibrated the quantitative engine confidence using sample quality and edge strength.
- Added report-level analysis quality diagnostics.
- Added no-lookahead walk-forward backtesting and a CSV runner.
- Added deterministic regression tests for conflict handling and future-data isolation.
