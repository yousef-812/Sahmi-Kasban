from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def build_engine(database_url: str | None = None) -> Engine:
    settings = get_settings()
    url = database_url or settings.database_url
    common: dict[str, object] = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        common["connect_args"] = {"check_same_thread": False}
    else:
        common["pool_size"] = settings.database_pool_size
        common["max_overflow"] = settings.database_max_overflow
    return create_engine(url, **common)


engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def database_is_ready(db: Session) -> bool:
    db.execute(text("SELECT 1"))
    return True
