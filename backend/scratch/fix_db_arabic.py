from app.db.session import SessionLocal
from app.models import MarketInstrumentCatalog

db = SessionLocal()
kora = db.query(MarketInstrumentCatalog).filter(MarketInstrumentCatalog.ticker == "KORA").first()
if kora:
    kora.description = "كورة كورا كورة للإدارة والحسابات Korra"
    kora.active = True
    db.commit()
    print("FIXED KORA DESCRIPTION:", kora.ticker, kora.description, kora.active)
