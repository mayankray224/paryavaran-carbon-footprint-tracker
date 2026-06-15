"""
Shared test fixtures and database configuration for the Paryavaran test suite.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from sqlalchemy.pool import StaticPool
from src.models.database import Base, get_db
from run import app

# In-memory SQLite for isolated test runs
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Creates and drops tables before/after each individual test to guarantee isolated states.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Overrides the database session dependency inside the FastAPI app with the test session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client: TestClient) -> dict:
    """
    Helper fixture that registers and logs in a test user, returning auth header dict.
    """
    user_payload = {
        "username": "testuser",
        "password": "testpassword123"
    }
    # Register
    client.post("/api/auth/register", json=user_payload)
    # Login
    res = client.post("/api/auth/login", json=user_payload)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
