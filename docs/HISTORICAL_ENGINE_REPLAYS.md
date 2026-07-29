# Historical engine replays

Administrators can run a bounded historical replay from the mobile administration area.

## Safety contract

- A run covers at most 31 calendar days.
- The analysis for a target session can only see candles strictly before that session.
- Five stocks are processed concurrently; persistence and counters are serialized.
- Jobs, ticker tasks, and daily rows are persisted in PostgreSQL.
- Leaving the app does not stop the server worker.
- A stale running ticker is returned to the queue after ten minutes, allowing restart recovery.
- Recent sessions without the requested forward horizon remain `pending_evaluation`; they are not counted as failures.
- Every job is visible and downloadable only by the administrator account that created it.

## API

- `POST /api/v1/admin/operations/historical-replays/jobs`
- `GET /api/v1/admin/operations/historical-replays/jobs`
- `GET /api/v1/admin/operations/historical-replays/jobs/{job_id}`
- `GET /api/v1/admin/operations/historical-replays/jobs/{job_id}/export.csv`

## Server export

Run from the backend application directory inside the Fly machine:

```bash
python -m app.cli.export_historical_replay \
  --job-id REPLAY_JOB_UUID \
  --output /tmp/sahmi-engine-replay.csv
```

The CSV includes the frozen engine version, every engine result, aggregate signal and confidence, trade plan, quality diagnostics, future return, maximum upside, maximum drawdown, correctness, and failure details.
