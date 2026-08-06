from __future__ import annotations

import asyncio

from app.db.session import SessionLocal
from app.services.monetization import catalog_payload
from app.services.operations_settings import runtime_monetization_settings


def main() -> None:
    with SessionLocal() as db:
        settings = runtime_monetization_settings(db)
        payload = catalog_payload(settings)
        packs = payload.get("coin_packs", [])
        print(f"coin_packs_count={len(packs)}")
        for pack in packs:
            print(pack)


if __name__ == "__main__":
    asyncio.run(main())
