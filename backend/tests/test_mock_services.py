"""
Tests for mock services endpoints
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


# Create a test client for the mock endpoints
@pytest.fixture
def mock_client():
    """Create test client with mock services enabled"""
    # Temporarily enable mock services for testing
    from app.core.config import settings

    original_use_mock = settings.USE_MOCK_SERVICES
    settings.USE_MOCK_SERVICES = True

    # Reload app to include mock router
    from app.api.mock import mock_router

    app.include_router(mock_router, prefix="/mock")

    client = TestClient(app)
    yield client

    # Restore original setting
    settings.USE_MOCK_SERVICES = original_use_mock


class TestMockMarketCheck:
    """Tests for mock Market Check API endpoints"""

    def test_mock_car_search_no_filters(self, mock_client):
        """Test car search without filters returns all mock vehicles"""
        response = mock_client.post("/mock/marketcheck/search", json={})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "top_vehicles" in data
        assert "total_found" in data
        assert "search_criteria" in data
        assert len(data["top_vehicles"]) <= 5  # Returns max 5 vehicles

    def test_mock_car_search_with_make(self, mock_client):
        """Test car search filters by make"""
        response = mock_client.post("/mock/marketcheck/search", json={"make": "Honda"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify all returned vehicles match the make
        for vehicle in data["top_vehicles"]:
            assert vehicle["make"].lower() == "honda"

    def test_mock_car_search_with_budget(self, mock_client):
        """Test car search filters by budget range"""
        min_budget = 25000
        max_budget = 40000

        response = mock_client.post(
            "/mock/marketcheck/search",
            json={"budget_min": min_budget, "budget_max": max_budget},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify all returned vehicles are within budget
        for vehicle in data["top_vehicles"]:
            assert min_budget <= vehicle["price"] <= max_budget

    def test_mock_car_search_with_year_range(self, mock_client):
        """Test car search filters by year range"""
        response = mock_client.post(
            "/mock/marketcheck/search", json={"year_min": 2022, "year_max": 2023}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify all returned vehicles are within year range
        for vehicle in data["top_vehicles"]:
            assert 2022 <= vehicle["year"] <= 2023

    def test_mock_car_search_includes_metadata(self, mock_client):
        """Test car search includes recommendation metadata"""
        response = mock_client.post("/mock/marketcheck/search", json={})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify metadata fields are present
        for vehicle in data["top_vehicles"]:
            assert "recommendation_score" in vehicle
            assert "highlights" in vehicle
            assert "recommendation_summary" in vehicle


class TestMockLLM:
    """Tests for mock LLM API endpoints"""

    def test_mock_llm_generate_text(self, mock_client):
        """Test LLM text generation"""
        response = mock_client.post(
            "/mock/llm/generate",
            json={"prompt_id": "negotiation", "variables": {"round_number": 1}},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "content" in data
        assert "prompt_id" in data
        assert "model" in data
        assert isinstance(data["content"], str)
        assert data["prompt_id"] == "negotiation"

    def test_mock_llm_generate_structured_evaluation(self, mock_client):
        """Test LLM structured JSON generation for evaluation"""
        response = mock_client.post(
            "/mock/llm/generate-structured",
            json={
                "prompt_id": "evaluation",
                "variables": {"asking_price": 30000, "vin": "1HGCM82633A123456"},
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "content" in data
        content = data["content"]

        # Verify structured evaluation fields
        assert isinstance(content, dict)
        assert "fair_value" in content
        assert "score" in content
        assert "insights" in content
        assert "talking_points" in content
        assert isinstance(content["insights"], list)
        assert isinstance(content["talking_points"], list)

    def test_mock_llm_generate_structured_selection(self, mock_client):
        """Test LLM structured JSON generation for selection"""
        response = mock_client.post(
            "/mock/llm/generate-structured",
            json={"prompt_id": "selection", "variables": {}},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        content = data["content"]
        assert "recommendations" in content
        assert isinstance(content["recommendations"], list)

        # Verify recommendation structure
        if content["recommendations"]:
            rec = content["recommendations"][0]
            assert "index" in rec
            assert "score" in rec
            assert "highlights" in rec
            assert "summary" in rec


class TestMockNegotiation:
    """Tests for mock Negotiation API endpoints"""

    def test_mock_create_negotiation(self, mock_client):
        """Test creating a negotiation session"""
        response = mock_client.post(
            "/mock/negotiation/create",
            json={"deal_id": 1, "user_target_price": 28000, "strategy": "moderate"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "session_id" in data
        assert "status" in data
        assert "current_round" in data
        assert "agent_message" in data
        assert data["status"] == "active"
        assert data["current_round"] == 1

    def test_mock_create_negotiation_missing_fields(self, mock_client):
        """Test creating negotiation without required fields fails"""
        response = mock_client.post("/mock/negotiation/create", json={})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_mock_process_next_round_counter(self, mock_client):
        """Test processing next round with counter offer"""
        # First create a session
        create_response = mock_client.post(
            "/mock/negotiation/create",
            json={"deal_id": 1, "user_target_price": 28000},
        )
        session_id = create_response.json()["session_id"]

        # Process next round with counter
        response = mock_client.post(
            f"/mock/negotiation/{session_id}/next",
            json={"user_action": "counter", "counter_offer": 27000},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["session_id"] == session_id
        assert data["current_round"] == 2
        assert "agent_message" in data
        assert "metadata" in data

    def test_mock_process_next_round_confirm(self, mock_client):
        """Test processing next round with confirmation"""
        # Create session
        create_response = mock_client.post(
            "/mock/negotiation/create",
            json={"deal_id": 1, "user_target_price": 28000},
        )
        session_id = create_response.json()["session_id"]

        # Confirm the deal
        response = mock_client.post(
            f"/mock/negotiation/{session_id}/next", json={"user_action": "confirm"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "completed"

    def test_mock_process_next_round_reject(self, mock_client):
        """Test processing next round with rejection"""
        # Create session
        create_response = mock_client.post(
            "/mock/negotiation/create",
            json={"deal_id": 1, "user_target_price": 28000},
        )
        session_id = create_response.json()["session_id"]

        # Reject the deal
        response = mock_client.post(
            f"/mock/negotiation/{session_id}/next", json={"user_action": "reject"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "cancelled"

    def test_mock_get_negotiation(self, mock_client):
        """Test retrieving a negotiation session"""
        # Create session
        create_response = mock_client.post(
            "/mock/negotiation/create",
            json={"deal_id": 1, "user_target_price": 28000},
        )
        session_id = create_response.json()["session_id"]

        # Get session
        response = mock_client.get(f"/mock/negotiation/{session_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["session_id"] == session_id
        assert "deal_id" in data
        assert "status" in data
        assert "messages" in data

    def test_mock_get_nonexistent_negotiation(self, mock_client):
        """Test retrieving non-existent negotiation returns 404"""
        response = mock_client.get("/mock/negotiation/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestMockEvaluation:
    """Tests for mock Deal Evaluation API endpoints"""

    def test_mock_evaluate_deal(self, mock_client):
        """Test deal evaluation"""
        response = mock_client.post(
            "/mock/evaluation/evaluate",
            json={
                "vehicle_vin": "1HGCM82633A123456",
                "asking_price": 30000,
                "condition": "good",
                "mileage": 50000,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "fair_value" in data
        assert "score" in data
        assert "insights" in data
        assert "talking_points" in data
        assert isinstance(data["insights"], list)
        assert isinstance(data["talking_points"], list)
        assert 1.0 <= data["score"] <= 10.0

    def test_mock_evaluate_deal_adjusts_score_by_condition(self, mock_client):
        """Test that evaluation score varies by condition"""
        # Test excellent condition
        response_excellent = mock_client.post(
            "/mock/evaluation/evaluate",
            json={
                "vehicle_vin": "TEST123",
                "asking_price": 30000,
                "condition": "excellent",
                "mileage": 10000,
            },
        )

        # Test poor condition
        response_poor = mock_client.post(
            "/mock/evaluation/evaluate",
            json={
                "vehicle_vin": "TEST123",
                "asking_price": 30000,
                "condition": "poor",
                "mileage": 150000,
            },
        )

        excellent_score = response_excellent.json()["score"]
        poor_score = response_poor.json()["score"]

        # Excellent condition should have higher score
        assert excellent_score > poor_score

    def test_mock_start_evaluation_pipeline(self, mock_client):
        """Test starting evaluation pipeline"""
        response = mock_client.post("/mock/evaluation/pipeline/start", json={"deal_id": 1})

        assert response.status_code == 200
        data = response.json()

        assert "evaluation_id" in data
        assert "deal_id" in data
        assert "status" in data
        assert "current_step" in data
        assert "step_result" in data
        assert data["status"] == "analyzing"

        # Verify step result includes questions
        step_result = data["step_result"]
        assert "questions" in step_result
        assert isinstance(step_result["questions"], list)

    def test_mock_submit_evaluation_answers(self, mock_client):
        """Test submitting evaluation answers"""
        # Start pipeline first
        start_response = mock_client.post("/mock/evaluation/pipeline/start", json={"deal_id": 1})
        evaluation_id = start_response.json()["evaluation_id"]

        # Submit answers
        response = mock_client.post(
            f"/mock/evaluation/pipeline/{evaluation_id}/submit",
            json={"answers": {"exterior_condition": "Good", "interior_condition": "Good"}},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["evaluation_id"] == evaluation_id
        assert data["status"] == "completed"
        assert "result_json" in data
        assert data["result_json"] is not None

        # Verify result structure
        result = data["result_json"]
        assert "overall_score" in result
        assert "fair_value" in result
        assert "recommendation" in result


class TestMockHealth:
    """Tests for mock services health check"""

    def test_mock_health_check(self, mock_client):
        """Test mock services health check endpoint"""
        response = mock_client.get("/mock/marketcheck/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["status"] == "healthy"
        assert "endpoints" in data
        assert data["service"] == "mock_services"
