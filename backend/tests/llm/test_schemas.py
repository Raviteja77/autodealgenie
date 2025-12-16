"""Test LLM schemas"""

import pytest
from pydantic import ValidationError

from app.llm.schemas import LLMError, LLMRequest, LLMResponse


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
