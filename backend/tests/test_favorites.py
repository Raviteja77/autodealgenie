"""Test favorites endpoints"""

import pytest

from app.api.dependencies import get_current_user
from app.models.models import Favorite, User


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


@pytest.fixture(autouse=True)
def clear_favorites(db):
    """Clear favorites from database before each test"""
    db.query(Favorite).delete()
    db.commit()
    yield
    db.query(Favorite).delete()
    db.commit()


@pytest.fixture
def sample_favorite_data():
    """Sample favorite data for testing"""
    return {
        "vin": "1HGBH41JXMN109186",
        "make": "Toyota",
        "model": "Camry",
        "year": 2022,
        "price": 25000.00,
        "mileage": 15000,
        "fuel_type": "Gasoline",
        "location": "Los Angeles, CA",
        "color": "Silver",
        "condition": "Used",
        "image": "https://example.com/car.jpg",
    }


def test_add_favorite(authenticated_client, sample_favorite_data):
    """Test adding a favorite"""
    response = authenticated_client.post(
        "/api/v1/favorites/", json=sample_favorite_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["vin"] == sample_favorite_data["vin"]
    assert data["make"] == sample_favorite_data["make"]
    assert data["model"] == sample_favorite_data["model"]
    assert data["year"] == sample_favorite_data["year"]
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


def test_add_duplicate_favorite(authenticated_client, sample_favorite_data):
    """Test adding a duplicate favorite (should fail)"""
    # Add favorite first time
    response1 = authenticated_client.post(
        "/api/v1/favorites/", json=sample_favorite_data
    )
    assert response1.status_code == 201

    # Try to add same favorite again
    response2 = authenticated_client.post(
        "/api/v1/favorites/", json=sample_favorite_data
    )
    assert response2.status_code == 400
    assert "already in favorites" in response2.json()["detail"].lower()


def test_get_favorites_empty(authenticated_client):
    """Test getting favorites when none exist"""
    response = authenticated_client.get("/api/v1/favorites/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_favorites(authenticated_client, sample_favorite_data):
    """Test getting all favorites"""
    # Add a favorite
    add_response = authenticated_client.post(
        "/api/v1/favorites/", json=sample_favorite_data
    )
    assert add_response.status_code == 201

    # Get all favorites
    response = authenticated_client.get("/api/v1/favorites/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["vin"] == sample_favorite_data["vin"]


def test_get_favorite_by_vin(authenticated_client, sample_favorite_data):
    """Test getting a specific favorite by VIN"""
    # Add a favorite
    add_response = authenticated_client.post(
        "/api/v1/favorites/", json=sample_favorite_data
    )
    assert add_response.status_code == 201

    # Get specific favorite
    vin = sample_favorite_data["vin"]
    response = authenticated_client.get(f"/api/v1/favorites/{vin}")

    assert response.status_code == 200
    data = response.json()
    assert data["vin"] == vin


def test_get_favorite_not_found(authenticated_client):
    """Test getting a favorite that doesn't exist"""
    response = authenticated_client.get("/api/v1/favorites/NONEXISTENTVIN123")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_remove_favorite(authenticated_client, sample_favorite_data):
    """Test removing a favorite"""
    # Add a favorite
    add_response = authenticated_client.post(
        "/api/v1/favorites/", json=sample_favorite_data
    )
    assert add_response.status_code == 201

    # Remove the favorite
    vin = sample_favorite_data["vin"]
    response = authenticated_client.delete(f"/api/v1/favorites/{vin}")

    assert response.status_code == 204

    # Verify it's removed
    get_response = authenticated_client.get(f"/api/v1/favorites/{vin}")
    assert get_response.status_code == 404


def test_remove_favorite_not_found(authenticated_client):
    """Test removing a favorite that doesn't exist"""
    response = authenticated_client.delete("/api/v1/favorites/NONEXISTENTVIN123")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_favorites_require_authentication(client, sample_favorite_data):
    """Test that favorites endpoints require authentication"""
    # Try to add favorite without auth
    response = client.post("/api/v1/favorites/", json=sample_favorite_data)
    assert response.status_code == 401

    # Try to get favorites without auth
    response = client.get("/api/v1/favorites/")
    assert response.status_code == 401

    # Try to get specific favorite without auth
    response = client.get("/api/v1/favorites/SOMEVIN123")
    assert response.status_code == 401

    # Try to delete favorite without auth
    response = client.delete("/api/v1/favorites/SOMEVIN123")
    assert response.status_code == 401
