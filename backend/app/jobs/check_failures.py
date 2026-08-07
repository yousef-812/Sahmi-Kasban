from app.db.session import SessionLocal
from app.models import MarketScanRun
from sqlalchemy import select

def main():
    db = SessionLocal()
    runs = db.scalars(
        select(MarketScanRun).where(MarketScanRun.status == "failed").order_by(MarketScanRun.source_session_date.desc()).limit(5)
    ).all()
    for r in runs:
        print(f"Date: {r.source_session_date} | Status: {r.status}")
        print("Details:")
        print(r.details)
        print("-" * 50)
    db.close()

if __name__ == '__main__':
    main()
