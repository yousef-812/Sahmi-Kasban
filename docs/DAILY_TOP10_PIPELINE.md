# Daily EGX Top 10 Pipeline

## Purpose

The backend creates one immutable report for the next EGX trading session. The public wording is:

> الأسهم الأعلى تقييمًا وفق التحليل الآلي للجلسة القادمة

The report is an automated decision-support output, not a guarantee of profit or an execution instruction.

## Scheduling

Run the job at 5:00 PM in `Africa/Cairo` after the final daily candles are expected to be available:

```bash
cd backend
python -m app.jobs.generate_daily_top10
```

Example Linux cron entry:

```cron
0 17 * * 0-4 cd /app/backend && /app/.venv/bin/python -m app.jobs.generate_daily_top10
```

The job still validates the day and time internally. Calling it early, on Friday/Saturday, or on a configured holiday returns a skipped status without creating a report.

## Holiday maintenance

`EGX_HOLIDAYS` is a comma-separated list of ISO dates:

```text
EGX_HOLIDAYS=2026-01-07,2026-04-13,2026-04-25
```

Operations must reconcile this value with the official exchange holiday calendar before production deployment and whenever the exchange publishes changes.

A second safety gate requires each stock's last daily candle to match the source session date. Therefore, a missing or delayed final close cannot silently become a published report.

## Universe and eligibility

The current universe is the deduplicated EGX seed registry. Before production, it must be reconciled with a licensed authoritative instrument feed.

Each symbol must pass:

- minimum historical candle count;
- final-candle date equal to the source session;
- configured 20-session average turnover threshold;
- configured non-zero-volume ratio;
- successful core-engine analysis;
- a final `BUY` or `WATCH` signal.

The defaults are configurable:

```text
DAILY_SCAN_MAX_CONCURRENCY=4
DAILY_SCAN_MIN_AVERAGE_TURNOVER_EGP=1000000
DAILY_SCAN_MIN_NONZERO_VOLUME_RATIO=0.80
DAILY_REPORT_SIZE=10
```

If fewer than 10 eligible candidates are produced, no report is published. The scan is marked failed with audit details.

## Ranking

Candidates are ordered deterministically by:

1. qualification status;
2. signal priority (`BUY` before `WATCH`);
3. final score;
4. confidence;
5. average turnover.

AI does not select or rank stocks. It only explains the already-selected top candidates. If AI is unavailable, a deterministic Arabic explanation is stored.

## Atomic persistence

The following are committed together:

- the complete `market_reports` record;
- exactly 10 `market_report_items`;
- the completed `market_scan_runs` audit record.

A database failure rolls the transaction back. Failed scans keep an audit record but do not expose or sell a partial report.

## User access and charging

Preview endpoint:

```text
GET /api/v1/market/reports/latest/preview
```

The preview includes dates, market summary, item count, cost, and whether the current user has unlocked the report. It does not include ticker names or item payloads.

Unlock endpoint:

```text
POST /api/v1/market/reports/{report_id}/unlock
```

Full report endpoint:

```text
GET /api/v1/market/reports/{report_id}
```

Unlocking costs 100 internal points, displayed as 1.00 coin. A unique `(user_id, report_id)` record and an idempotent wallet transaction prevent duplicate charging. The debit and unlock record are committed in the same database transaction.

An incomplete or missing report is never charged.

## Audit tables

### `market_scan_runs`

Stores source and target sessions, schedule, timestamps, status, universe counts, failure counts, exclusions, and the resulting report ID.

### `market_report_unlocks`

Stores one unlock per user/report and the exact wallet transaction ID used for the debit.

## Operational checks

Before trusting a production report, verify:

- the source session date matches the latest candles;
- exactly 10 items exist with unique ranks 1–10;
- the scan status is `complete`;
- the target date is the next configured trading session;
- no provider or engine failure rate is abnormally high;
- `EGX_HOLIDAYS` is current;
- historical results are retained, including negative outcomes.
