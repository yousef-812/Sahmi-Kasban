# Performance Experience

PR #19 exposes the server-authoritative Performance Ledger from PR #18 through transparent APIs, Flutter screens, and administrator controls.

## Public windows

Authenticated users may request the latest 7 or 30 due EGX report sessions. A session becomes due only after its configured Cairo close gate. The response includes every due report found in the window, even when its market data is incomplete.

The aggregate response reports:

- sessions found and sessions fully evaluated;
- total, completed, pending, and failed outcomes;
- explicit data-completeness percentage;
- positive, negative, and flat result counts;
- average and median close return in integer basis points;
- direction accuracy, target hit rates, and stop-loss touch rate;
- best and worst observed outcomes;
- rank-by-rank results for positions 1 through 10;
- a session history that preserves partial and failed states.

Negative outcomes are valid completed observations and are never excluded from calculations. Rates use only outcomes where the relevant fact exists, while completeness always uses the frozen report-item count as its denominator.

## Public endpoints

- `GET /api/v1/market/performance/summary?window=7`
- `GET /api/v1/market/performance/summary?window=30`
- `GET /api/v1/market/performance/reports`
- `GET /api/v1/market/performance/reports/{report_id}`

No public endpoint requires unlocking the original paid report. Performance history is a transparency surface and does not reveal the original analysis payload beyond the frozen ticker, rank, measured prices, and outcome facts.

## Flutter experience

The application includes:

- a performance entry in the authenticated dashboard;
- a 7-session/30-session selector;
- visible completeness and delayed-data counts;
- average, median, positive/negative counts, direction accuracy, targets, and stop loss;
- best and worst outcomes;
- rank 1–10 comparison;
- report history and per-report outcome details;
- visible correction counts and revision history.

The interface explicitly states that past results do not guarantee future performance.

## Benchmark boundary

The response exposes an explicit `benchmark.status=not_available` record for EGX30. PR #19 does not fabricate or approximate an index comparison because an authoritative benchmark-session ledger has not been implemented yet.

## Administrator operations

Administrators can:

- list reports that have not completed all frozen outcomes;
- run the due-report evaluator in batches;
- retry a specific incomplete report;
- export the latest 7 or 30 sessions as CSV;
- correct an outcome using supplied official OHLC evidence.

Administrator endpoints remain protected by the existing server-side administrator dependency.

## Audited corrections

Corrections never overwrite history silently. Each correction:

1. locks the target outcome;
2. validates positive OHLC values and the high/low range;
3. stores the complete pre-correction payload;
4. recomputes return, upside, drawdown, direction, target, and stop facts using the ledger formulas;
5. stores the complete post-correction payload;
6. creates an incrementing `MarketReportOutcomeRevision`;
7. records the administrator, reason, provider, fingerprint, and timestamp;
8. refreshes the parent evaluation counts and status;
9. writes a `CommunityAdminEvent` audit event.

The report detail endpoint returns the revision history to authenticated users.

## CSV export

CSV export includes completed, pending, and failed outcomes. It contains report/session identity, ticker, rank, OHLC, returns, deterministic flags, provider evidence, evaluator version, and correction count. It intentionally retains negative and incomplete rows.
