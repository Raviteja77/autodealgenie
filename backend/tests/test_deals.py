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


def test_search_deal_by_email_and_vin(authenticated_client, mock_user):
    """Test searching for a deal by customer email and vehicle VIN"""
    # First create a deal
    deal_data = {
        "customer_name": "Search Test",
        "customer_email": mock_user.email,  # Use authenticated user's email
        "vehicle_make": "Tesla",
        "vehicle_model": "Model 3",
        "vehicle_vin": "5YJ3E1EA1KF123456",
        "vehicle_year": 2023,
        "vehicle_mileage": 5000,
        "asking_price": 45000.00,
        "status": "pending",
    }

    create_response = authenticated_client.post("/api/v1/deals/", json=deal_data)
    assert create_response.status_code == 201
    created_deal = create_response.json()

    # Search for the deal using email and VIN
    response = authenticated_client.get(
        f"/api/v1/deals/search?customer_email={deal_data['customer_email']}&vehicle_vin={deal_data['vehicle_vin']}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_deal["id"]
    assert data["customer_email"] == deal_data["customer_email"]
    assert data["vehicle_vin"] == deal_data["vehicle_vin"]


def test_search_nonexistent_deal(authenticated_client, mock_user):
    """Test searching for a non-existent deal returns 404"""
    response = authenticated_client.get(
        f"/api/v1/deals/search?customer_email={mock_user.email}&vehicle_vin=NONEXISTENT12345"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_search_deal_unauthorized_access(authenticated_client, mock_user):
    """Test that users cannot search deals for other users' emails"""
    # Create a deal with a different email
    deal_data = {
        "customer_name": "Other User",
        "customer_email": "otheruser@example.com",  # Different from mock_user.email
        "vehicle_make": "BMW",
        "vehicle_model": "X5",
        "vehicle_vin": "WBAJW7C51HG456789",
        "vehicle_year": 2022,
        "vehicle_mileage": 10000,
        "asking_price": 55000.00,
        "status": "pending",
    }

    create_response = authenticated_client.post("/api/v1/deals/", json=deal_data)
    assert create_response.status_code == 201

    # Try to search for it with authenticated user (should be forbidden)
    response = authenticated_client.get(
        f"/api/v1/deals/search?customer_email={deal_data['customer_email']}&vehicle_vin={deal_data['vehicle_vin']}"
    )
    assert response.status_code == 403
    data = response.json()
    assert "permission" in data["detail"].lower()


def test_search_deal_filters_correctly(authenticated_client, mock_user):
    """Test that the search correctly filters by both email and VIN"""
    # Create two deals with same VIN but different emails
    deal1_data = {
        "customer_name": "User One",
        "customer_email": mock_user.email,
        "vehicle_make": "Honda",
        "vehicle_model": "Civic",
        "vehicle_vin": "2HGFC2F59MH123456",
        "vehicle_year": 2021,
        "vehicle_mileage": 15000,
        "asking_price": 22000.00,
        "status": "pending",
    }

    # Create first deal
    create_response1 = authenticated_client.post("/api/v1/deals/", json=deal1_data)
    assert create_response1.status_code == 201
    deal1 = create_response1.json()

    # Search with correct email and VIN should find the deal
    response = authenticated_client.get(
        f"/api/v1/deals/search?customer_email={deal1_data['customer_email']}&vehicle_vin={deal1_data['vehicle_vin']}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == deal1["id"]

    # Search with correct email but wrong VIN should return 404
    response = authenticated_client.get(
        f"/api/v1/deals/search?customer_email={deal1_data['customer_email']}&vehicle_vin=WRONGVIN123456"
    )
    assert response.status_code == 404
