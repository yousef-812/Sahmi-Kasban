# Core V2 and walk-forward backtesting

## What changed

Core V2 keeps the existing deterministic engines but changes how their evidence is combined:

- every engine weight is discounted by its own confidence;
- disagreement is measured as weighted score dispersion;
- mixed bullish and bearish engines reduce both score strength and confidence;
- a BUY signal requires at least three bullish directional engines and no bearish engine;
- high-risk or low-confidence BUY results are downgraded to WATCH;
- the quantitative engine reports its sample size and calibrates confidence using sample quality and edge strength.

The report now contains an `analysis_quality` object with the raw aggregate, calibrated score,
consensus, dispersion, directional engine groups, failed engines, and conflict state. This data is
intended for diagnostics and transparent evaluation, not as a separate trading signal.

## Backtesting

`walk_forward_backtest` freezes the history at each cutoff, runs the analyzer using only that
history, and evaluates the signal on the following completed sessions. Future candles are never
passed to the analyzer.

```python
from sahmi_kasban import walk_forward_backtest

summary = walk_forward_backtest(
    "COMI",
    candles,
    min_train_size=200,
    horizon_sessions=5,
    step_sessions=5,
)
print(summary.to_dict(include_results=False))
```

A CSV can also be evaluated from the repository root:

```bash
python scripts/run_core_backtest.py data/comi.csv \
  --ticker COMI \
  --horizon-sessions 5 \
  --step-sessions 5 \
  --summary-only
```

The CSV must include `open`, `high`, `low`, `close`, and `volume`; `timestamp` is recommended.

## Metrics

The summary retains all observations, including negative outcomes, and reports:

- BUY, WATCH, and AVOID counts;
- directional accuracy;
- hit rate by signal;
- average and median forward return;
- average BUY return and drawdown;
- BUY profit factor when at least one losing BUY observation exists.

These metrics are historical measurements, not promises of future performance.
