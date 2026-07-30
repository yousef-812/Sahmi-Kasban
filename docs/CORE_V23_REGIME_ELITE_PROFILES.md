# Core v2.3: regime-aware elite opportunity profiles

Core v2.3 keeps the Core v2.2 directional weights and BUY/WATCH/AVOID thresholds. It changes the quality layer, market context, short-horizon trade plan, and provider-health universe.

## Why

Seven historical replay windows showed that one fixed elite gate was too conservative during confirmed speculative breakouts but was useful for protecting capital in weaker regimes. The median elite excess return was not consistently positive, so Core v2.3 does not weaken the balanced gate globally and does not force an elite label every day.

## Market context

`market-regime-v2.3` publishes a causal, trailing-only profile for each analyzed stock:

- `trend_bullish`
- `breakout_bullish`
- `speculative_bullish`
- `trend_bearish`
- `risk_off_volatile`
- `sideways_rotation`
- `mixed_volatile`

The daily report also derives `top-basket-regime-v2.3` from the selected basket. This is a selection context, not a substitute for an official EGX index or sector-breadth feed.

## Balanced elite

The balanced path retains the Core v2.2 requirements:

- BUY and qualified;
- score at least 80 and confidence at least 70;
- four bullish directional engines, no bearish engine and no conflict;
- bullish stock regime and bullish timeframe alignment;
- 20-session return no greater than 30%;
- trading continuity.

ATR and total-risk limits now adapt conservatively to 20-session turnover and market regime. More liquid shares may receive a small allowance, while bearish regimes tighten the limits.

## Aggressive elite

The aggressive path is independent; it does not relax the balanced path. It requires:

- all common directional, qualification, confidence, regime and timeframe gates;
- average turnover of at least EGP 5 million;
- a close 0.5% to 12% above the previous 20-session high;
- volume at least 1.5 times the 20-session average;
- positive 5-session momentum no greater than 20%;
- 20-session momentum between 5% and 45%;
- RSI between 50 and 82;
- adaptive ATR and total-risk budgets;
- stricter zero-volume continuity.

The label is exposed only when the top-ranked basket is `broad_bullish` or `speculative_bullish`. The report recommends half position size for aggressive opportunities.

## Five-session trade plan

The old default targets of 2R and 3.5R were rarely reached in five sessions. Core v2.3 uses:

- balanced: 1R and 1.75R;
- confirmed aggressive breakout: 1.25R and 2R.

The stop remains based on two ATR units. These are planning levels, not guaranteed exits.

## Provider-health universe

A symbol is excluded from automated scans and new replay jobs when it is:

- an ISIN-like scanner alias rather than a tradable ticker; or
- associated with at least three `MarketDataUnavailableError` replay failures and no replay with evaluated rows.

One transient failure never quarantines a symbol. Any evaluated replay success prevents quarantine. The scanner can rediscover listed symbols, so the API scan and isolated replay worker reapply health filtering after catalog refresh.

## Validation

The new tests cover:

- balanced adaptive limits;
- aggressive breakout, volume, liquidity and risk requirements;
- rejection of unconfirmed high-ATR moves;
- market-regime profile publication;
- five-session target ratios;
- report-level aggressive activation and half position plan;
- repeated provider failure quarantine and recovery;
- preservation of legacy Core v2.2 report payloads.

Core v2.3 still requires fresh replay windows after deployment. Historical Core v2.2 CSV files do not become Core v2.3 results retroactively.
