from __future__ import annotations

from app.db.session import SessionLocal
from app.models import AnalysisReplayJob

def main():
    db = SessionLocal()
    try:
        jobs = db.query(AnalysisReplayJob).order_by(AnalysisReplayJob.start_date).all()
        print(f"Total jobs: {len(jobs)}")
        for j in jobs:
            print(f"[{j.status.upper()}] {j.start_date} -> {j.end_date} | Rows: {j.completed_rows}/{j.total_rows} | Job ID: {j.id}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
