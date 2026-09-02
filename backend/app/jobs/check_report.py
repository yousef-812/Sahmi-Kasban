from app.db.session import SessionLocal
from app.models import MarketReport


def main():
    db = SessionLocal()
    r = db.query(MarketReport).order_by(MarketReport.target_session_date.desc()).first()
    if r:
        print("Verification details:")
        print(f"Title: {r.market_summary.get('title')}")
        print(f"Model: {r.market_summary.get('selection_model')}")
        print(f"Regime: {r.market_summary.get('selection_regime')}")
        print(f"Gate Version: {r.market_summary.get('elite_gate_version')}")
        print(f"Tiers: {r.market_summary.get('opportunity_tiers')}")
    else:
        print("No reports found!")
    db.close()


if __name__ == "__main__":
    main()
