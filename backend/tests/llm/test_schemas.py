"""Test LLM schemas"""

import pytest
from pydantic import ValidationError

from app.llm.schemas import (
    CarSelectionItem,
    CarSelectionResponse,
    DealEvaluation,
    LLMError,
    LLMRequest,
    LLMResponse,
)


class TestLLMRequest:
    """Test LLMRequest schema"""

    def test_llm_request_basic(self):
        """Test creating a basic LLM request"""
        request = LLMRequest(prompt_id="car_recommendation", variables={"budget": 30000})

        assert request.prompt_id == "car_recommendation"
        assert request.variables == {"budget": 30000}
        assert request.temperature == 0.7  # Default
        assert request.max_tokens is None
        assert request.model is None

    def test_llm_request_with_all_fields(self):
        """Test creating an LLM request with all fields"""
        request = LLMRequest(
            prompt_id="negotiation",
            variables={"make": "Honda", "model": "Accord"},
            model="gpt-4",
            temperature=0.5,
            max_tokens=500,
        )

        assert request.prompt_id == "negotiation"
        assert request.variables == {"make": "Honda", "model": "Accord"}
        assert request.model == "gpt-4"
        assert request.temperature == 0.5
        assert request.max_tokens == 500

    def test_llm_request_temperature_validation(self):
        """Test temperature validation (must be 0-2)"""
        # Valid temperatures
        LLMRequest(prompt_id="test", variables={}, temperature=0.0)
        LLMRequest(prompt_id="test", variables={}, temperature=1.0)
        LLMRequest(prompt_id="test", variables={}, temperature=2.0)

        # Invalid temperature (too low)
        with pytest.raises(ValidationError):
            LLMRequest(prompt_id="test", variables={}, temperature=-0.1)

        # Invalid temperature (too high)
        with pytest.raises(ValidationError):
            LLMRequest(prompt_id="test", variables={}, temperature=2.1)

    def test_llm_request_max_tokens_validation(self):
        """Test max_tokens validation (must be positive)"""
        # Valid max_tokens
        LLMRequest(prompt_id="test", variables={}, max_tokens=100)

        # Invalid max_tokens (zero)
        with pytest.raises(ValidationError):
            LLMRequest(prompt_id="test", variables={}, max_tokens=0)

        # Invalid max_tokens (negative)
        with pytest.raises(ValidationError):
            LLMRequest(prompt_id="test", variables={}, max_tokens=-100)

    def test_llm_request_empty_variables(self):
        """Test LLM request with empty variables"""
        request = LLMRequest(prompt_id="test", variables={})
        assert request.variables == {}

    def test_llm_request_default_variables(self):
        """Test LLM request with default variables"""
        request = LLMRequest(prompt_id="test")
        assert request.variables == {}


class TestLLMResponse:
    """Test LLMResponse schema"""

    def test_llm_response_text_content(self):
        """Test LLM response with text content"""
        response = LLMResponse(
            content="This is a test response", prompt_id="test", model="gpt-4", tokens_used=50
        )

        assert response.content == "This is a test response"
        assert response.prompt_id == "test"
        assert response.model == "gpt-4"
        assert response.tokens_used == 50

    def test_llm_response_dict_content(self):
        """Test LLM response with dictionary content"""
        content_dict = {"fair_value": 25000, "score": 7.5, "insights": ["Good deal"]}
        response = LLMResponse(
            content=content_dict, prompt_id="evaluation", model="gpt-4", tokens_used=100
        )

        assert response.content == content_dict
        assert isinstance(response.content, dict)
        assert response.content["fair_value"] == 25000

    def test_llm_response_without_tokens(self):
        """Test LLM response without token count"""
        response = LLMResponse(content="Test", prompt_id="test", model="gpt-4")

        assert response.tokens_used is None


class TestLLMError:
    """Test LLMError schema"""

    def test_llm_error_basic(self):
        """Test creating a basic LLM error"""
        error = LLMError(error_type="api_error", message="OpenAI API failed")

        assert error.error_type == "api_error"
        assert error.message == "OpenAI API failed"
        assert error.details is None

    def test_llm_error_with_details(self):
        """Test creating an LLM error with details"""
        error = LLMError(
            error_type="validation_error",
            message="Invalid response format",
            details={"field": "fair_value", "expected": "float", "got": "string"},
        )

        assert error.error_type == "validation_error"
        assert error.message == "Invalid response format"
        assert error.details["field"] == "fair_value"
        assert error.details["expected"] == "float"


class TestCarSelectionItem:
    """Test CarSelectionItem schema"""

    def test_car_selection_item_basic(self):
        """Test creating a basic car selection item"""
        item = CarSelectionItem(
            index=0,
            score=8.5,
            highlights=["Great fuel economy", "Low mileage", "Recent model year"],
            summary="Excellent value for reliable transportation",
        )

        assert item.index == 0
        assert item.score == 8.5
        assert len(item.highlights) == 3
        assert item.highlights[0] == "Great fuel economy"
        assert item.summary == "Excellent value for reliable transportation"

    def test_car_selection_item_with_all_fields(self):
        """Test creating a car selection item with all fields"""
        item = CarSelectionItem(
            index=2,
            score=9.2,
            highlights=["Excellent safety ratings", "Low maintenance costs", "Good resale value"],
            summary="Top choice for family vehicle with strong safety features",
        )

        assert item.index == 2
        assert item.score == 9.2
        assert len(item.highlights) == 3
        assert "Excellent safety ratings" in item.highlights
        assert item.summary == "Top choice for family vehicle with strong safety features"

    def test_car_selection_item_validation(self):
        """Test validation of required fields"""
        # Missing required fields should raise ValidationError
        with pytest.raises(ValidationError):
            CarSelectionItem(index=0, score=8.0)  # Missing highlights and summary

        with pytest.raises(ValidationError):
            CarSelectionItem(
                index=0, highlights=["Good value"], summary="Great car"
            )  # Missing score

    def test_car_selection_item_score_types(self):
        """Test that score accepts both int and float"""
        item_float = CarSelectionItem(
            index=0, score=8.5, highlights=["Good"], summary="Nice car"
        )
        item_int = CarSelectionItem(index=1, score=9, highlights=["Great"], summary="Best car")

        assert item_float.score == 8.5
        assert item_int.score == 9

    def test_car_selection_item_empty_highlights(self):
        """Test car selection item with empty highlights list"""
        item = CarSelectionItem(index=0, score=7.0, highlights=[], summary="Basic option")

        assert item.highlights == []
        assert len(item.highlights) == 0


class TestCarSelectionResponse:
    """Test CarSelectionResponse schema"""

    def test_car_selection_response_basic(self):
        """Test creating a basic car selection response"""
        items = [
            CarSelectionItem(
                index=0,
                score=8.5,
                highlights=["Great fuel economy", "Low mileage", "Recent model year"],
                summary="Excellent value",
            ),
            CarSelectionItem(
                index=2,
                score=9.0,
                highlights=["Top safety ratings", "Reliable brand", "Good warranty"],
                summary="Best overall choice",
            ),
        ]
        response = CarSelectionResponse(recommendations=items)

        assert len(response.recommendations) == 2
        assert response.recommendations[0].index == 0
        assert response.recommendations[1].index == 2
        assert response.recommendations[0].score == 8.5
        assert response.recommendations[1].score == 9.0

    def test_car_selection_response_single_item(self):
        """Test car selection response with single recommendation"""
        item = CarSelectionItem(
            index=0, score=7.5, highlights=["Good value"], summary="Solid choice"
        )
        response = CarSelectionResponse(recommendations=[item])

        assert len(response.recommendations) == 1
        assert response.recommendations[0].score == 7.5

    def test_car_selection_response_empty(self):
        """Test car selection response with empty recommendations"""
        response = CarSelectionResponse(recommendations=[])

        assert len(response.recommendations) == 0
        assert response.recommendations == []

    def test_car_selection_response_validation(self):
        """Test validation of required fields"""
        # Missing required field should raise ValidationError
        with pytest.raises(ValidationError):
            CarSelectionResponse()  # Missing recommendations

    def test_car_selection_response_multiple_items(self):
        """Test car selection response with multiple recommendations"""
        items = [
            CarSelectionItem(index=i, score=8.0 + i * 0.5, highlights=[f"Feature {i}"], summary=f"Car {i}")
            for i in range(5)
        ]
        response = CarSelectionResponse(recommendations=items)

        assert len(response.recommendations) == 5
        assert response.recommendations[0].score == 8.0
        assert response.recommendations[4].score == 10.0
        assert all(item.index == i for i, item in enumerate(response.recommendations))


class TestDealEvaluation:
    """Test DealEvaluation schema"""

    def test_deal_evaluation_basic(self):
        """Test creating a basic deal evaluation"""
        evaluation = DealEvaluation(
            fair_value=25000.00,
            score=7.5,
            insights=["Priced above market", "Good condition", "Average mileage"],
            talking_points=["Request maintenance records", "Point out comparable vehicles", "Negotiate warranty"],
        )

        assert evaluation.fair_value == 25000.00
        assert evaluation.score == 7.5
        assert len(evaluation.insights) == 3
        assert len(evaluation.talking_points) == 3

    def test_deal_evaluation_score_validation(self):
        """Test score validation (must be 1-10)"""
        # Valid scores
        DealEvaluation(
            fair_value=20000, score=1.0, insights=["Good"], talking_points=["Talk"]
        )
        DealEvaluation(
            fair_value=20000, score=10.0, insights=["Good"], talking_points=["Talk"]
        )

        # Invalid score (too low)
        with pytest.raises(ValidationError):
            DealEvaluation(
                fair_value=20000, score=0.5, insights=["Good"], talking_points=["Talk"]
            )

        # Invalid score (too high)
        with pytest.raises(ValidationError):
            DealEvaluation(
                fair_value=20000, score=10.5, insights=["Good"], talking_points=["Talk"]
            )

    def test_deal_evaluation_required_fields(self):
        """Test validation of required fields"""
        # Missing required fields should raise ValidationError
        with pytest.raises(ValidationError):
            DealEvaluation(fair_value=20000, score=7.5)  # Missing insights and talking_points

    def test_deal_evaluation_empty_lists(self):
        """Test deal evaluation with empty insight/talking point lists"""
        evaluation = DealEvaluation(
            fair_value=30000.00,
            score=8.0,
            insights=[],
            talking_points=[],
        )

        assert evaluation.fair_value == 30000.00
        assert evaluation.score == 8.0
        assert evaluation.insights == []
        assert evaluation.talking_points == []

    def test_deal_evaluation_multiple_items(self):
        """Test deal evaluation with multiple insights and talking points"""
        insights = [f"Insight {i}" for i in range(5)]
        talking_points = [f"Point {i}" for i in range(5)]

        evaluation = DealEvaluation(
            fair_value=28500.50,
            score=6.8,
            insights=insights,
            talking_points=talking_points,
        )

        assert len(evaluation.insights) == 5
        assert len(evaluation.talking_points) == 5
        assert evaluation.fair_value == 28500.50
        assert evaluation.score == 6.8
