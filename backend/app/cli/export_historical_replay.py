from __future__ import annotations

import argparse
from pathlib import Path
from uuid import UUID

from app.db.session import SessionLocal
from app.models import AnalysisReplayJob
from app.services.historical_replays import build_historical_replay_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export one persisted historical engine replay as UTF-8 CSV."
    )
    parser.add_argument("--job-id", required=True, type=UUID)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with SessionLocal() as db:
        job = db.get(AnalysisReplayJob, args.job_id)
        if job is None:
            raise SystemExit(f"Replay job not found: {args.job_id}")
        payload = build_historical_replay_csv(db, job=job)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(
        f"Exported replay {args.job_id} to {args.output} "
        f"({len(payload)} bytes, status={job.status})"
    )


if __name__ == "__main__":
    main()
