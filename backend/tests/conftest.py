from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models as _models  # noqa: F401
from app.core.security import create_email_verification_reference
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.services.email import get_account_email_service

engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class FakeAccountEmailService:
    def __init__(self) -> None:
        self.verification_tokens: dict[str, str] = {}
        self.verification_codes: dict[str, str] = {}
        self.password_reset_tokens: dict[str, str] = {}

    def send_email_verification(self, email: str, code: str) -> None:
        self.verification_codes[email] = code
        self.verification_tokens[email] = create_email_verification_reference(
            email=email,
            code=code,
        )

    def send_password_reset(self, email: str, token: str) -> None:
        self.password_reset_tokens[email] = token


@pytest.fixture(scope="session", autouse=True)
def database_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    yield session
    session.close()
    cleanup = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            cleanup.execute(table.delete())
        cleanup.commit()
    finally:
        cleanup.close()


@pytest.fixture
def fake_email_service() -> FakeAccountEmailService:
    return FakeAccountEmailService()


@pytest.fixture
def client(
    db_session: Session,
    fake_email_service: FakeAccountEmailService,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_account_email_service] = lambda: fake_email_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
