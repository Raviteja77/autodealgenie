"""Test deal endpoints"""

import pytest

from app.api.dependencies import get_current_user
from app.models.models import User


@pytest.fixture
def mock_user(db):
    """Create a mock user for testing"""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="hashed",
        full_name="Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client, mock_user):
    """Override the get_current_user dependency to return mock user"""
    from app.main import app

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides.clear()


def test_create_deal(authenticated_client):
    """Test creating a deal"""
    deal_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_vin": "1HGCM41JXMN109186",
        "vehicle_year": 2022,
        "vehicle_mileage": 15000,
        "asking_price": 25000.00,
        "status": "pending",
    }

    response = authenticated_client.post("/api/v1/deals/", json=deal_data)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == deal_data["customer_name"]
    assert data["customer_email"] == deal_data["customer_email"]
    assert "id" in data


def test_get_deals(authenticated_client):
    """Test getting all deals"""
    response = authenticated_client.get("/api/v1/deals/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_deal(authenticated_client):
    """Test getting a specific deal"""
    # First create a deal
    deal_data = {
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "vehicle_make": "Honda",
        "vehicle_model": "Accord",
        "vehicle_vin": "1HGCM41JXMN109186",
        "vehicle_year": 2021,
        "vehicle_mileage": 20000,
        "asking_price": 23000.00,
        "status": "pending",
    }

    create_response = authenticated_client.post("/api/v1/deals/", json=deal_data)
    assert create_response.status_code == 201
    deal_id = create_response.json()["id"]

    # Now get the deal
    response = authenticated_client.get(f"/api/v1/deals/{deal_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == deal_id
    assert data["customer_name"] == deal_data["customer_name"]


def test_get_nonexistent_deal(authenticated_client):
    """Test getting a non-existent deal"""
    response = authenticated_client.get("/api/v1/deals/99999")
    assert response.status_code == 404


def test_update_deal(authenticated_client):
    """Test updating a deal"""
    # First create a deal
    deal_data = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "vehicle_make": "Ford",
        "vehicle_model": "F-150",
        "vehicle_vin": "1HGCM41JXMN109186",
        "vehicle_year": 2020,
        "vehicle_mileage": 30000,
        "asking_price": 35000.00,
        "status": "pending",
    }

    create_response = authenticated_client.post("/api/v1/deals/", json=deal_data)
    assert create_response.status_code == 201
    deal_id = create_response.json()["id"]

    # Update the deal
    update_data = {
        "status": "in_progress",
        "offer_price": 33000.00,
        "notes": "Negotiating price",
    }

    response = authenticated_client.put(f"/api/v1/deals/{deal_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == deal_id
    assert data["status"] == "in_progress"
    assert data["offer_price"] == 33000.00
    assert data["notes"] == "Negotiating price"


def test_update_nonexistent_deal(authenticated_client):
    """Test updating a non-existent deal"""
    update_data = {
        "status": "completed",
    }

    response = authenticated_client.put("/api/v1/deals/99999", json=update_data)
    assert response.status_code == 404


def test_delete_deal(authenticated_client):
    """Test deleting a deal"""
    # First create a deal
    deal_data = {
        "customer_name": "Delete Test",
        "customer_email": "delete@example.com",
        "vehicle_make": "Chevrolet",
        "vehicle_model": "Silverado",
        "vehicle_vin": "1HGCM41JXMN109186",
        "vehicle_year": 2019,
        "vehicle_mileage": 40000,
        "asking_price": 30000.00,
        "status": "pending",
    }

    create_response = authenticated_client.post("/api/v1/deals/", json=deal_data)
    assert create_response.status_code == 201
    deal_id = create_response.json()["id"]

    # Delete the deal
    response = authenticated_client.delete(f"/api/v1/deals/{deal_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = authenticated_client.get(f"/api/v1/deals/{deal_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_deal(authenticated_client):
    """Test deleting a non-existent deal"""
    response = authenticated_client.delete("/api/v1/deals/99999")
    assert response.status_code == 404
