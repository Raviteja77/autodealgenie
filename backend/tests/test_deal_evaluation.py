"""Test deal evaluation service and endpoint"""

from unittest.mock import AsyncMock, patch

import pytest

from app.api.dependencies import get_current_user
from app.llm.schemas import DealEvaluation
from app.models.models import User
from app.services.deal_evaluation_service import DealEvaluationService


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
def mock_llm_evaluation():
    """Mock DealEvaluation response"""
    return DealEvaluation(
        fair_value=24500.00,
        score=7.5,
        insights=[
            "This vehicle is priced $500 above market value",
            "The mileage is average for this year",
            "Condition rating suggests proper maintenance",
        ],
        talking_points=[
            "Point out comparable vehicles priced at $24,500",
            "Request maintenance records to justify the condition rating",
            "Use the mileage as slight negotiation leverage",
        ],
    )


class TestDealEvaluationService:
    """Test DealEvaluationService class"""

    @pytest.mark.asyncio
    async def test_evaluate_deal_with_llm(self, mock_llm_evaluation):
        """Test deal evaluation with LLM available"""
        service = DealEvaluationService()

        with patch("app.llm.llm_client.llm_client") as mock_client:
            mock_client.is_available.return_value = True
            mock_client.generate_structured_json.return_value = mock_llm_evaluation

            with patch("app.services.deal_evaluation_service.generate_structured_json") as mock_gen:
                mock_gen.return_value = mock_llm_evaluation

                result = await service.evaluate_deal(
                    vehicle_vin="1HGBH41JXMN109186",
                    asking_price=25000.00,
                    condition="good",
                    mileage=45000,
                )

                assert "fair_value" in result
                assert "score" in result
                assert "insights" in result
                assert "talking_points" in result

                assert isinstance(result["fair_value"], float)
                assert 1.0 <= result["score"] <= 10.0
                assert isinstance(result["insights"], list)
                assert isinstance(result["talking_points"], list)
                assert len(result["insights"]) > 0
                assert len(result["talking_points"]) > 0

    @pytest.mark.asyncio
    async def test_evaluate_deal_fallback(self):
        """Test deal evaluation fallback when LLM is not available"""
        service = DealEvaluationService()

        with patch("app.llm.llm_client.llm_client") as mock_client:
            mock_client.is_available.return_value = False

            result = await service.evaluate_deal(
                vehicle_vin="1HGBH41JXMN109186",
                asking_price=25000.00,
                condition="excellent",
                mileage=15000,
            )

            assert "fair_value" in result
            assert "score" in result
            assert "insights" in result
            assert "talking_points" in result

            # Check that score is reasonable for excellent condition and low mileage
            assert result["score"] >= 6.0
            assert isinstance(result["insights"], list)
            assert len(result["insights"]) > 0

    @pytest.mark.asyncio
    async def test_fallback_evaluation_excellent_condition(self):
        """Test fallback evaluation with excellent condition"""
        service = DealEvaluationService()

        result = service._fallback_evaluation(
            vehicle_vin="1HGBH41JXMN109186",
            asking_price=30000.00,
            condition="excellent",
            mileage=20000,
        )

        # Excellent condition + low mileage should get high score
        assert result["score"] >= 7.0
        assert result["fair_value"] > 0
        assert (
            "excellent" in " ".join(result["insights"]).lower()
            or "low mileage" in " ".join(result["insights"]).lower()
        )

    @pytest.mark.asyncio
    async def test_fallback_evaluation_poor_condition(self):
        """Test fallback evaluation with poor condition"""
        service = DealEvaluationService()

        result = service._fallback_evaluation(
            vehicle_vin="1HGBH41JXMN109186",
            asking_price=15000.00,
            condition="poor",
            mileage=180000,
        )

        # Poor condition + high mileage should get lower score
        assert result["score"] <= 5.0
        assert len(result["insights"]) > 0
        assert len(result["talking_points"]) > 0

    @pytest.mark.asyncio
    async def test_evaluate_deal_with_llm_error(self, mock_llm_evaluation):
        """Test deal evaluation handles LLM errors gracefully"""
        service = DealEvaluationService()

        with patch("app.services.deal_evaluation_service.generate_structured_json") as mock_gen:
            # Mock generate_structured_json to raise an exception
            mock_gen.side_effect = Exception("LLM API Error")

            with patch("app.llm.llm_client.llm_client") as mock_client:
                mock_client.is_available.return_value = True

                result = await service.evaluate_deal(
                    vehicle_vin="1HGBH41JXMN109186",
                    asking_price=25000.00,
                    condition="good",
                    mileage=50000,
                )

                # Should fall back to basic evaluation
                assert "fair_value" in result
                assert "score" in result
                assert 1.0 <= result["score"] <= 10.0

    @pytest.mark.asyncio
    async def test_evaluate_deal_with_invalid_json(self):
        """Test deal evaluation handles invalid responses from LLM"""
        service = DealEvaluationService()

        with patch("app.services.deal_evaluation_service.generate_structured_json") as mock_gen:
            # Mock invalid response
            mock_gen.side_effect = ValueError("Invalid JSON")

            with patch("app.llm.llm_client.llm_client") as mock_client:
                mock_client.is_available.return_value = True

                result = await service.evaluate_deal(
                    vehicle_vin="1HGBH41JXMN109186",
                    asking_price=25000.00,
                    condition="good",
                    mileage=50000,
                )

                # Should fall back to basic evaluation
                assert "fair_value" in result
                assert "score" in result
                assert 1.0 <= result["score"] <= 10.0


class TestDealEvaluationEndpoint:
    """Test /api/v1/deals/evaluate endpoint"""

    def test_evaluate_deal_endpoint_success(self, authenticated_client):
        """Test successful deal evaluation via API endpoint"""
        evaluation_data = {
            "vehicle_vin": "1HGBH41JXMN109186",
            "asking_price": 25000.00,
            "condition": "good",
            "mileage": 45000,
        }

        with patch("app.llm.llm_client.llm_client") as mock_client:
            mock_client.is_available.return_value = False  # Use fallback for predictable results

            response = authenticated_client.post("/api/v1/deals/evaluate", json=evaluation_data)

            assert response.status_code == 200
            data = response.json()

            assert "fair_value" in data
            assert "score" in data
            assert "insights" in data
            assert "talking_points" in data

            assert data["fair_value"] > 0
            assert 1.0 <= data["score"] <= 10.0
            assert isinstance(data["insights"], list)
            assert isinstance(data["talking_points"], list)

    def test_evaluate_deal_endpoint_requires_auth(self, client):
        """Test that evaluation endpoint requires authentication"""
        evaluation_data = {
            "vehicle_vin": "1HGBH41JXMN109186",
            "asking_price": 25000.00,
            "condition": "good",
            "mileage": 45000,
        }

        response = client.post("/api/v1/deals/evaluate", json=evaluation_data)
        assert response.status_code == 401

    def test_evaluate_deal_endpoint_invalid_vin(self, authenticated_client):
        """Test evaluation endpoint with invalid VIN length"""
        evaluation_data = {
            "vehicle_vin": "SHORT",  # Invalid VIN (too short)
            "asking_price": 25000.00,
            "condition": "good",
            "mileage": 45000,
        }

        response = authenticated_client.post("/api/v1/deals/evaluate", json=evaluation_data)
        assert response.status_code == 422  # Validation error

    def test_evaluate_deal_endpoint_invalid_price(self, authenticated_client):
        """Test evaluation endpoint with invalid price"""
        evaluation_data = {
            "vehicle_vin": "1HGBH41JXMN109186",
            "asking_price": -1000.00,  # Invalid: negative price
            "condition": "good",
            "mileage": 45000,
        }

        response = authenticated_client.post("/api/v1/deals/evaluate", json=evaluation_data)
        assert response.status_code == 422  # Validation error

    def test_evaluate_deal_endpoint_invalid_mileage(self, authenticated_client):
        """Test evaluation endpoint with invalid mileage"""
        evaluation_data = {
            "vehicle_vin": "1HGBH41JXMN109186",
            "asking_price": 25000.00,
            "condition": "good",
            "mileage": -5000,  # Invalid: negative mileage
        }

        response = authenticated_client.post("/api/v1/deals/evaluate", json=evaluation_data)
        assert response.status_code == 422  # Validation error

    def test_evaluate_deal_endpoint_missing_fields(self, authenticated_client):
        """Test evaluation endpoint with missing required fields"""
        evaluation_data = {
            "vehicle_vin": "1HGBH41JXMN109186",
            # Missing asking_price, condition, mileage
        }

        response = authenticated_client.post("/api/v1/deals/evaluate", json=evaluation_data)
        assert response.status_code == 422  # Validation error


class TestDealEvaluationCaching:
    """Test Redis caching functionality in deal evaluation"""

    @pytest.mark.asyncio
    async def test_cache_key_generation_deterministic(self):
        """Test that cache key generation is deterministic"""
        service = DealEvaluationService()

        key1 = service._generate_cache_key(
            vehicle_vin="1HGBH41JXMN109186",
            asking_price=25000.00,
            condition="good",
            mileage=45000,
            make="Honda",
            model="Accord",
            year=2020,
        )

        key2 = service._generate_cache_key(
            vehicle_vin="1HGBH41JXMN109186",
            asking_price=25000.00,
            condition="good",
            mileage=45000,
            make="Honda",
            model="Accord",
            year=2020,
        )

        # Same inputs should produce same cache key
        assert key1 == key2

    @pytest.mark.asyncio
    async def test_cache_key_different_for_different_params(self):
        """Test that cache keys differ when parameters change"""
        service = DealEvaluationService()

        key1 = service._generate_cache_key(
            vehicle_vin="1HGBH41JXMN109186",
            asking_price=25000.00,
            condition="good",
            mileage=45000,
        )

        # Different VIN
        key2 = service._generate_cache_key(
            vehicle_vin="2HGBH41JXMN109187",
            asking_price=25000.00,
            condition="good",
            mileage=45000,
        )

        # Different price
        key3 = service._generate_cache_key(
            vehicle_vin="1HGBH41JXMN109186",
            asking_price=24500.00,
            condition="good",
            mileage=45000,
        )

        # Different condition
        key4 = service._generate_cache_key(
            vehicle_vin="1HGBH41JXMN109186",
            asking_price=25000.00,
            condition="excellent",
            mileage=45000,
        )

        # Different mileage
        key5 = service._generate_cache_key(
            vehicle_vin="1HGBH41JXMN109186",
            asking_price=25000.00,
            condition="good",
            mileage=50000,
        )

        # All keys should be different
        keys = [key1, key2, key3, key4, key5]
        assert len(keys) == len(set(keys))

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_data(self, mock_llm_evaluation):
        """Test that cached data is returned on cache hit without calling LLM"""
        service = DealEvaluationService()

        with patch("app.db.redis.redis_client") as mock_redis_client:
            mock_redis = AsyncMock()
            mock_redis.get.return_value = '{"fair_value": 24000.0, "score": 8.0, "insights": ["Cached insight"], "talking_points": ["Cached point"]}'
            mock_redis_client.get_client.return_value = mock_redis

            with patch("app.llm.llm_client.llm_client") as mock_client:
                mock_client.is_available.return_value = True

                with patch(
                    "app.services.deal_evaluation_service.generate_structured_json"
                ) as mock_gen:
                    # LLM should NOT be called on cache hit
                    mock_gen.return_value = mock_llm_evaluation

                    result = await service.evaluate_deal(
                        vehicle_vin="1HGBH41JXMN109186",
                        asking_price=25000.00,
                        condition="good",
                        mileage=45000,
                    )

                    # Should return cached data
                    assert result["fair_value"] == 24000.0
                    assert result["score"] == 8.0

                    # LLM should NOT have been called
                    mock_gen.assert_not_called()

    @pytest.mark.asyncio
    async def test_cache_miss_calls_llm_and_caches(self, mock_llm_evaluation):
        """Test that LLM is called on cache miss and result is cached"""
        service = DealEvaluationService()

        with patch("app.db.redis.redis_client") as mock_redis_client:
            mock_redis = AsyncMock()
            mock_redis.get = AsyncMock(return_value=None)  # Ensure get returns None
            mock_redis.setex = AsyncMock(return_value=True)
            mock_redis_client.get_client.return_value = mock_redis

            with patch("app.llm.llm_client.llm_client") as mock_client:
                mock_client.is_available.return_value = True

                with patch(
                    "app.services.deal_evaluation_service.generate_structured_json"
                ) as mock_gen:
                    mock_gen.return_value = mock_llm_evaluation

                    result = await service.evaluate_deal(
                        vehicle_vin="1HGBH41JXMN109186",
                        asking_price=25000.00,
                        condition="good",
                        mileage=45000,
                    )

                    # LLM should have been called
                    mock_gen.assert_called_once()

                    # Result should be cached
                    mock_redis.setex.assert_called_once()
                    assert result["fair_value"] == 24500.00
                    assert result["score"] == 7.5

    @pytest.mark.asyncio
    async def test_cache_unavailable_graceful_degradation(self, mock_llm_evaluation):
        """Test graceful degradation when Redis is unavailable"""
        service = DealEvaluationService()

        with patch("app.db.redis.redis_client") as mock_redis_client:
            # Redis not available
            mock_redis_client.get_client.return_value = None

            with patch("app.llm.llm_client.llm_client") as mock_client:
                mock_client.is_available.return_value = True

                with patch(
                    "app.services.deal_evaluation_service.generate_structured_json"
                ) as mock_gen:
                    mock_gen.return_value = mock_llm_evaluation

                    result = await service.evaluate_deal(
                        vehicle_vin="1HGBH41JXMN109186",
                        asking_price=25000.00,
                        condition="good",
                        mileage=45000,
                    )

                    # LLM should still be called
                    mock_gen.assert_called_once()
                    assert result["fair_value"] == 24500.00
