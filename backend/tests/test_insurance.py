"""
Integration tests for Insurance API endpoints
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app

# Test data
VALID_INSURANCE_REQUEST = {
    "vehicle_value": 25000.0,
    "vehicle_age": 3,
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "coverage_type": "full",
    "driver_age": 30,
}


@pytest.mark.asyncio
async def test_get_insurance_recommendations_success(mock_current_user):
    """Test successful insurance recommendations request"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=VALID_INSURANCE_REQUEST,
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "recommendations" in data
    assert "total_matches" in data
    assert "request_summary" in data
    assert isinstance(data["recommendations"], list)
    assert data["total_matches"] >= 0

    # If there are recommendations, check their structure
    if len(data["recommendations"]) > 0:
        rec = data["recommendations"][0]
        assert "provider" in rec
        assert "match_score" in rec
        assert "estimated_monthly_premium" in rec
        assert "estimated_annual_premium" in rec
        assert "recommendation_reason" in rec
        assert "rank" in rec


@pytest.mark.asyncio
async def test_get_insurance_recommendations_liability_coverage(mock_current_user):
    """Test insurance recommendations for liability coverage"""
    request_data = {
        **VALID_INSURANCE_REQUEST,
        "coverage_type": "liability",
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=request_data,
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_matches"] > 0


@pytest.mark.asyncio
async def test_get_insurance_recommendations_comprehensive_coverage(mock_current_user):
    """Test insurance recommendations for comprehensive coverage"""
    request_data = {
        **VALID_INSURANCE_REQUEST,
        "coverage_type": "comprehensive",
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=request_data,
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_matches"] > 0


@pytest.mark.asyncio
async def test_get_insurance_recommendations_young_driver(mock_current_user):
    """Test insurance recommendations for young driver"""
    request_data = {
        **VALID_INSURANCE_REQUEST,
        "driver_age": 19,
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=request_data,
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Should have some matches for young drivers
    assert data["total_matches"] > 0


@pytest.mark.asyncio
async def test_get_insurance_recommendations_senior_driver(mock_current_user):
    """Test insurance recommendations for senior driver"""
    request_data = {
        **VALID_INSURANCE_REQUEST,
        "driver_age": 70,
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=request_data,
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_matches"] > 0


@pytest.mark.asyncio
async def test_get_insurance_recommendations_high_value_vehicle(mock_current_user):
    """Test insurance recommendations for high-value vehicle"""
    request_data = {
        **VALID_INSURANCE_REQUEST,
        "vehicle_value": 80000.0,
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=request_data,
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total_matches"] > 0


@pytest.mark.asyncio
async def test_get_insurance_recommendations_invalid_coverage_type(mock_current_user):
    """Test insurance recommendations with invalid coverage type"""
    request_data = {
        **VALID_INSURANCE_REQUEST,
        "coverage_type": "invalid",
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=request_data,
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_insurance_recommendations_negative_vehicle_value(mock_current_user):
    """Test insurance recommendations with negative vehicle value"""
    request_data = {
        **VALID_INSURANCE_REQUEST,
        "vehicle_value": -1000.0,
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=request_data,
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_insurance_recommendations_invalid_driver_age(mock_current_user):
    """Test insurance recommendations with invalid driver age"""
    request_data = {
        **VALID_INSURANCE_REQUEST,
        "driver_age": 10,  # Too young
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=request_data,
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_insurance_recommendations_missing_required_field(mock_current_user):
    """Test insurance recommendations with missing required field"""
    request_data = {
        "vehicle_value": 25000.0,
        "vehicle_age": 3,
        # Missing vehicle_make, vehicle_model, coverage_type, driver_age
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=request_data,
        )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_insurance_recommendations_unauthorized():
    """Test insurance recommendations without authentication"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/insurance/recommendations",
            json=VALID_INSURANCE_REQUEST,
        )

    # Should require authentication
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
