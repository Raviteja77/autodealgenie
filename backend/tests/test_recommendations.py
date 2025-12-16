"""
Tests for car recommendation endpoints
"""

from unittest.mock import AsyncMock, MagicMock, patch

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


@pytest.fixture
def mock_rate_limiter_allowed():
    """Mock rate limiter that allows requests"""
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = MagicMock(return_value=None)
    mock_pipeline.zcard = MagicMock(return_value=None)
    mock_pipeline.zadd = MagicMock(return_value=None)
    mock_pipeline.expire = MagicMock(return_value=None)
    mock_pipeline.execute = AsyncMock(return_value=[None, 10, None, None])  # request count = 10

    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(return_value=mock_pipeline)
    mock_redis.zrange = AsyncMock(return_value=[])

    return mock_redis


@pytest.fixture
def mock_rate_limiter_exceeded():
    """Mock rate limiter that denies requests (rate limit exceeded)"""
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = MagicMock(return_value=None)
    mock_pipeline.zcard = MagicMock(return_value=None)
    mock_pipeline.zadd = MagicMock(return_value=None)
    mock_pipeline.expire = MagicMock(return_value=None)
    mock_pipeline.execute = AsyncMock(
        return_value=[None, 100, None, None]
    )  # request count = 100 (at limit)

    mock_redis = MagicMock()
    mock_redis.pipeline = MagicMock(return_value=mock_pipeline)
    mock_redis.zrange = AsyncMock(return_value=[[b"timestamp", 1234567890.0]])

    return mock_redis


@pytest.fixture
def mock_service_response():
    """Mock response from car recommendation service"""
    return {
        "search_criteria": {
            "make": "Toyota",
            "model": "RAV4",
            "price_min": 20000,
            "price_max": 30000,
            "condition": "used",
            "year_min": 2020,
            "year_max": 2024,
            "mileage_max": 50000,
            "location": "Seattle, WA",
        },
        "top_vehicles": [
            {
                "vin": "ABC123XYZ456",
                "make": "Toyota",
                "model": "RAV4",
                "year": 2022,
                "trim": "XLE Premium",
                "mileage": 25000,
                "price": 28500.00,
                "msrp": 35000.00,
                "location": "Seattle, WA",
                "dealer_name": "Seattle Toyota",
                "dealer_contact": "206-555-1234",
                "photo_links": ["https://example.com/photo1.jpg"],
                "vdp_url": "https://example.com/vehicle/123",
                "exterior_color": "White",
                "interior_color": "Black",
                "drivetrain": "AWD",
                "transmission": "Automatic",
                "engine": "2.5L I4",
                "fuel_type": "Gasoline",
                "carfax_1_owner": True,
                "carfax_clean_title": True,
                "inventory_type": "used",
                "days_on_market": 15,
                "recommendation_score": 9.2,
                "highlights": [
                    "Excellent value at $6,500 under MSRP",
                    "Low mileage for year",
                    "Clean Carfax, single owner",
                ],
                "recommendation_summary": "This Toyota RAV4 offers exceptional value with verified low mileage and clean history.",
            },
            {
                "vin": "DEF789GHI012",
                "make": "Toyota",
                "model": "RAV4",
                "year": 2021,
                "trim": "LE",
                "mileage": 35000,
                "price": 26000.00,
                "location": "Seattle, WA",
                "dealer_name": "Downtown Toyota",
                "recommendation_score": 8.5,
                "highlights": [
                    "Great price point",
                    "Well maintained",
                    "Popular trim level",
                ],
                "recommendation_summary": "Solid option with good value and reliability.",
            },
        ],
        "total_found": 45,
        "total_analyzed": 50,
    }


def test_get_car_recommendations_success(
    authenticated_client, mock_service_response, mock_rate_limiter_allowed
):
    """Test successful car recommendations request"""
    request_data = {
        "budget_min": 20000,
        "budget_max": 30000,
        "body_type": "suv",
        "must_have_features": ["AWD", "Backup Camera"],
        "location": "Seattle, WA",
        "make": "Toyota",
        "model": "RAV4",
        "year_min": 2020,
        "year_max": 2024,
        "mileage_max": 50000,
        "user_priorities": "Reliability and fuel efficiency",
    }

    with patch(
        "app.core.rate_limiter.redis_client.get_client", return_value=mock_rate_limiter_allowed
    ):
        with patch(
            "app.services.car_recommendation_service.car_recommendation_service.search_and_recommend",
            return_value=mock_service_response,
        ):
            response = authenticated_client.post("/api/v1/recommendations/cars", json=request_data)

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "recommendations" in data
            assert "total_found" in data
            assert "total_analyzed" in data
            assert "search_criteria" in data

            # Verify recommendations
            assert len(data["recommendations"]) == 2
            assert data["total_found"] == 45
            assert data["total_analyzed"] == 50

            # Verify first recommendation
            first_rec = data["recommendations"][0]
            assert first_rec["vin"] == "ABC123XYZ456"
            assert first_rec["make"] == "Toyota"
            assert first_rec["model"] == "RAV4"
            assert first_rec["recommendation_score"] == 9.2
            assert len(first_rec["highlights"]) == 3


def test_get_car_recommendations_minimal_input(
    authenticated_client, mock_service_response, mock_rate_limiter_allowed
):
    """Test car recommendations with minimal user input"""
    request_data = {
        "budget_max": 30000,
    }

    with patch(
        "app.core.rate_limiter.redis_client.get_client", return_value=mock_rate_limiter_allowed
    ):
        with patch(
            "app.services.car_recommendation_service.car_recommendation_service.search_and_recommend",
            return_value=mock_service_response,
        ):
            response = authenticated_client.post("/api/v1/recommendations/cars", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert "recommendations" in data


def test_get_car_recommendations_no_results(authenticated_client, mock_rate_limiter_allowed):
    """Test car recommendations when no vehicles found"""
    request_data = {
        "budget_min": 1000,
        "budget_max": 2000,
        "make": "Ferrari",
    }

    empty_response = {
        "search_criteria": {"make": "Ferrari", "price_min": 1000, "price_max": 2000},
        "top_vehicles": [],
        "total_found": 0,
        "total_analyzed": 0,
        "message": "No vehicles found matching your criteria.",
    }

    with patch(
        "app.core.rate_limiter.redis_client.get_client", return_value=mock_rate_limiter_allowed
    ):
        with patch(
            "app.services.car_recommendation_service.car_recommendation_service.search_and_recommend",
            return_value=empty_response,
        ):
            response = authenticated_client.post("/api/v1/recommendations/cars", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["total_found"] == 0
            assert len(data["recommendations"]) == 0
            assert data["message"] == "No vehicles found matching your criteria."


def test_get_car_recommendations_rate_limit_exceeded(
    authenticated_client, mock_rate_limiter_exceeded
):
    """Test rate limit enforcement"""
    request_data = {
        "budget_max": 30000,
        "make": "Toyota",
    }

    with patch(
        "app.core.rate_limiter.redis_client.get_client", return_value=mock_rate_limiter_exceeded
    ):
        response = authenticated_client.post("/api/v1/recommendations/cars", json=request_data)

        assert response.status_code == 429
        data = response.json()
        assert "Rate limit exceeded" in data["detail"]


def test_get_car_recommendations_validation_error(authenticated_client, mock_rate_limiter_allowed):
    """Test validation error handling"""
    request_data = {
        "budget_min": 20000,
        "budget_max": 30000,
    }

    with patch(
        "app.core.rate_limiter.redis_client.get_client", return_value=mock_rate_limiter_allowed
    ):
        with patch(
            "app.services.car_recommendation_service.car_recommendation_service.search_and_recommend",
            side_effect=ValueError("Invalid budget range"),
        ):
            response = authenticated_client.post("/api/v1/recommendations/cars", json=request_data)

            assert response.status_code == 400
            data = response.json()
            assert "Invalid request" in data["detail"]


def test_get_car_recommendations_connection_error(authenticated_client, mock_rate_limiter_allowed):
    """Test external API connection error handling"""
    request_data = {
        "make": "Toyota",
        "model": "RAV4",
    }

    with patch(
        "app.core.rate_limiter.redis_client.get_client", return_value=mock_rate_limiter_allowed
    ):
        with patch(
            "app.services.car_recommendation_service.car_recommendation_service.search_and_recommend",
            side_effect=ConnectionError("MarketCheck API unavailable"),
        ):
            response = authenticated_client.post("/api/v1/recommendations/cars", json=request_data)

            assert response.status_code == 503
            data = response.json()
            assert "temporarily unavailable" in data["detail"]


def test_get_car_recommendations_internal_error(authenticated_client, mock_rate_limiter_allowed):
    """Test internal server error handling"""
    request_data = {
        "make": "Toyota",
    }

    with patch(
        "app.core.rate_limiter.redis_client.get_client", return_value=mock_rate_limiter_allowed
    ):
        with patch(
            "app.services.car_recommendation_service.car_recommendation_service.search_and_recommend",
            side_effect=Exception("Unexpected error"),
        ):
            response = authenticated_client.post("/api/v1/recommendations/cars", json=request_data)

            assert response.status_code == 500
            data = response.json()
            assert "Failed to retrieve car recommendations" in data["detail"]


def test_get_car_recommendations_unauthorized(client):
    """Test unauthorized access (no authentication)"""
    request_data = {
        "make": "Toyota",
        "budget_max": 30000,
    }

    response = client.post("/api/v1/recommendations/cars", json=request_data)

    assert response.status_code == 401
    data = response.json()
    assert "Not authenticated" in data["detail"]


def test_get_car_recommendations_with_all_preferences(
    authenticated_client, mock_service_response, mock_rate_limiter_allowed
):
    """Test car recommendations with all preference fields"""
    request_data = {
        "budget_min": 20000,
        "budget_max": 30000,
        "body_type": "suv",
        "must_have_features": ["AWD", "Backup Camera", "Bluetooth", "Leather Seats"],
        "location": "Seattle, WA",
        "make": "Toyota",
        "model": "RAV4",
        "year_min": 2020,
        "year_max": 2024,
        "mileage_max": 50000,
        "user_priorities": "Looking for a reliable family SUV with modern safety features",
    }

    with patch(
        "app.core.rate_limiter.redis_client.get_client", return_value=mock_rate_limiter_allowed
    ):
        with patch(
            "app.services.car_recommendation_service.car_recommendation_service.search_and_recommend",
            return_value=mock_service_response,
        ) as mock_search:
            response = authenticated_client.post("/api/v1/recommendations/cars", json=request_data)

            assert response.status_code == 200

            # Verify service was called with correct parameters
            mock_search.assert_called_once()
            call_kwargs = mock_search.call_args.kwargs
            assert call_kwargs["make"] == "Toyota"
            assert call_kwargs["model"] == "RAV4"
            assert call_kwargs["budget_min"] == 20000
            assert call_kwargs["budget_max"] == 30000
            assert call_kwargs["car_type"] == "suv"
            assert call_kwargs["year_min"] == 2020
            assert call_kwargs["year_max"] == 2024
            assert call_kwargs["mileage_max"] == 50000
            assert "family SUV" in call_kwargs["user_priorities"]


def test_user_preference_input_invalid_budget_range():
    """Test that invalid budget range is rejected"""
    import pytest
    from pydantic import ValidationError

    from app.schemas.car_recommendation import UserPreferenceInput

    with pytest.raises(ValidationError) as exc_info:
        UserPreferenceInput(
            budget_min=30000,
            budget_max=20000,  # Max less than min
        )

    assert "budget_max must be greater than budget_min" in str(exc_info.value)


def test_user_preference_input_invalid_year_range():
    """Test that invalid year range is rejected"""
    import pytest
    from pydantic import ValidationError

    from app.schemas.car_recommendation import UserPreferenceInput

    with pytest.raises(ValidationError) as exc_info:
        UserPreferenceInput(
            year_min=2024,
            year_max=2020,  # Max less than min
        )

    assert "year_max must be greater than or equal to year_min" in str(exc_info.value)


def test_user_preference_input_valid_ranges():
    """Test that valid ranges are accepted"""
    from app.schemas.car_recommendation import UserPreferenceInput

    # Valid budget range
    prefs = UserPreferenceInput(
        budget_min=20000,
        budget_max=30000,
        year_min=2020,
        year_max=2024,
    )
    assert prefs.budget_min == 20000
    assert prefs.budget_max == 30000
    assert prefs.year_min == 2020
    assert prefs.year_max == 2024


def test_must_have_features_integration(
    authenticated_client, mock_service_response, mock_rate_limiter_allowed
):
    """Test that must_have_features are incorporated into user_priorities"""
    request_data = {
        "budget_max": 30000,
        "must_have_features": ["AWD", "Backup Camera", "Bluetooth"],
        "user_priorities": "Looking for reliability",
    }

    with patch(
        "app.core.rate_limiter.redis_client.get_client", return_value=mock_rate_limiter_allowed
    ):
        with patch(
            "app.services.car_recommendation_service.car_recommendation_service.search_and_recommend",
            return_value=mock_service_response,
        ) as mock_search:
            response = authenticated_client.post("/api/v1/recommendations/cars", json=request_data)

            assert response.status_code == 200

            # Verify service was called with enhanced priorities
            mock_search.assert_called_once()
            call_kwargs = mock_search.call_args.kwargs
            user_priorities = call_kwargs["user_priorities"]

            # Should include both original priorities and must-have features
            assert "Looking for reliability" in user_priorities
            assert "Must-have features" in user_priorities
            assert "AWD" in user_priorities
            assert "Backup Camera" in user_priorities
            assert "Bluetooth" in user_priorities
