import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Order, IncidentLog


# ==========================================
# Test Database Configuration
# ==========================================

# Shared in-memory SQLite database.
# StaticPool ensures that all threads use
# the same SQLite connection.
SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# Create all database tables
Base.metadata.create_all(bind=test_engine)


# ==========================================
# Override FastAPI Database Dependency
# ==========================================

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ==========================================
# Test Client
# ==========================================

client = TestClient(app)


# ==========================================
# Tests
# ==========================================

@patch("app.api.orders.get_redis_client")
def test_create_and_get_order(mock_redis):
    # Disable Redis for this test.
    # The endpoint should use the test database directly.
    mock_redis.return_value = None

    order_payload = {
        "customer_email": "ops-lead@company.com",
        "item_name": "Cloud Compute Node",
        "quantity": 3,
        "total_amount": 299.99,
    }

    # Create order
    create_res = client.post(
        "/api/v1/orders",
        json=order_payload,
    )

    assert create_res.status_code == 201

    created_data = create_res.json()

    assert created_data["id"] is not None
    assert created_data["customer_email"] == "ops-lead@company.com"
    assert created_data["status"] == "CONFIRMED"

    order_id = created_data["id"]

    # Get created order
    get_res = client.get(
        f"/api/v1/orders/{order_id}"
    )

    assert get_res.status_code == 200
    assert get_res.json()["id"] == order_id


def test_get_nonexistent_order():
    res = client.get(
        "/api/v1/orders/999999"
    )

    assert res.status_code == 404