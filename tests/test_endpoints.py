# tests/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_full_dispute_flow(client):
    # Create customer
    customer = {
        "name": "Test User",
        "email": "test@example.com",
        "account_type": "Individual",
    }
    response = client.post("/api/v1/customers/", json=customer)
    assert response.status_code == 201
    customer_id = response.json()["id"]
    print(f"Customer ID: {customer_id}")
    # Create dispute
    dispute = {
        "customer_id": customer_id,
        "transaction_id": "TX123456",
        "merchant_name": "Test Merchant",
        "amount": 1500.0,
        "description": "Unauthorized transaction",
        "category": "Fraud",
    }
    response = client.post("/api/v1/disputes/", json=dispute)
    assert response.status_code == 201
    dispute_id = response.json()["id"]

    # Analyze dispute
    response = client.post(f"/api/v1/disputes/{dispute_id}/analyze")
    assert response.status_code == 201
    analysis = response.json()["analysis"]
    assert "priority" in analysis
    assert "risk_score" in analysis

    # Get dispute
    response = client.get(f"/api/v1/disputes/{dispute_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "Open"

    # Cleanup
    response = client.delete(f"/api/v1/disputes/{dispute_id}")
    assert response.status_code == 200
    # response = client.delete(f"/api/v1/customers/{customer_id}")
    # assert response.status_code == 200
