# Core v2.1 replay findings

Source replay: 2026-06-29 through 2026-07-29, five-session horizon.

## Dataset quality

- 5,071 exported rows.
- 3,951 evaluated rows across 17 evaluable analysis dates.
- 998 rows were still pending evaluation.
- 122 rows were skipped for insufficient history.
- The replay covered 290 tickers in the row export; provider-level failures for other ticker tasks must not be interpreted as engine failures.
- Adjacent five-session outcomes overlap, so rows are not independent observations. Weight learning must use date blocks and a longer replay horizon.

## Evidence used for v2.1

- BUY observations averaged 3.98% versus 3.65% for the evaluated universe.
- Equal-date BUY excess return averaged about 0.50 percentage points over five sessions and was positive on 14 of 17 dates.
- 1,088 quantitative probabilities were at least 99%; 394 were exactly 100%. The old `raw_edge * 6` mapping was overconfident.
- 863 of 909 evaluated AVOID rows were unqualified stocks. Qualification rejection is an eligibility decision, not a bearish forecast.
- Multi-timeframe score had the strongest mean daily rank relationship in this short replay. SMC was approximately neutral. This is not enough history to learn permanent weights.
- Risk score was useful for realized drawdown but weak for direction. It remains a gate and sizing input rather than part of the directional score.
- The existing five-session trade plan reached target 1 in roughly 14% of BUY observations and target 2 in roughly 4%. Horizon-specific trade-plan calibration requires a longer, non-overlapping replay.

## Safe changes

1. Calibrate the quantitative logistic mapping and remove the duplicated momentum score bump.
2. Build the directional score only from directional engines.
3. Keep qualification and risk as separate gates.
4. Qualify liquidity using average traded value in EGP, not raw share count.
5. Persist Fly memory at 1 GB so five-way replay batches do not revert to the 512 MB OOM configuration on deploy.

## Changes deliberately deferred

- No learned engine weights from this single month.
- No automatic threshold optimization from overlapping five-session labels.
- No SMC removal based on only 17 evaluable dates.
- No trade target change until several months of horizon-specific results are available.
