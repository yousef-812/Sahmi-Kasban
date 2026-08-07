from app.db.session import SessionLocal
from app.models import MarketReport

def main():
    db = SessionLocal()
    reports = db.query(MarketReport).order_by(MarketReport.target_session_date.desc()).all()
    print("Remote Database Market Report Sessions & Engine Versions:")
    print(f"{'Target Date':<15} | {'Source Date':<15} | {'Engine Version':<35} | {'Model':<45}")
    print("-" * 120)
    for r in reports:
        summary = r.market_summary or {}
        snapshot = r.source_snapshot or {}
        gate_version = summary.get("elite_gate_version", "unknown")
        model = summary.get("selection_model", "unknown")
        source_date = snapshot.get("source_session_date", "unknown")
        target_date = r.target_session_date.isoformat() if r.target_session_date else "unknown"
        print(f"{target_date:<15} | {source_date:<15} | {gate_version:<35} | {model:<45}")
    db.close()

if __name__ == '__main__':
    main()
