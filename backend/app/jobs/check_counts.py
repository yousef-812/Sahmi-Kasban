from app.db.session import SessionLocal
from app.models import MarketReport, MarketReportItem


def main():
    db = SessionLocal()
    reports = db.query(MarketReport).order_by(MarketReport.target_session_date.desc()).all()
    print("Report Counts:")
    for r in reports:
        cnt = db.query(MarketReportItem).filter_by(report_id=r.id).count()
        print(f"Target Date: {r.target_session_date} | Item Count: {cnt} | Status: {r.status}")
    db.close()

if __name__ == '__main__':
    main()
