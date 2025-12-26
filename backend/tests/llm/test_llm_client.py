"""Test LLM client functionality with synchronous OpenAI client"""

import json
from unittest.mock import MagicMock, patch

import pytest
from openai import APIError, APITimeoutError, AuthenticationError, RateLimitError
from pydantic import BaseModel, Field

from app.llm.llm_client import LLMClient
from app.utils.error_handler import ApiError


# Test Pydantic models
class DealEvaluation(BaseModel):
    """Test model for deal evaluation"""

    fair_value: float = Field(..., gt=0)
    score: float = Field(..., ge=1.0, le=10.0)
    insights: list[str] = Field(..., min_length=1)
    talking_points: list[str] = Field(..., min_length=1)


class CarRecommendation(BaseModel):
    """Test model for car recommendation"""

    make: str
    model: str
    price_range: str
    key_features: list[str]


@pytest.fixture
def mock_openai_client():
    """Mock synchronous OpenAI client"""
    client = MagicMock()
    return client


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_usage = MagicMock()

    mock_message.content = json.dumps(
        {
            "fair_value": 24500.0,
            "score": 7.5,
            "insights": ["Good mileage", "Fair price"],
            "talking_points": ["Ask for service history", "Check market comparables"],
        }
    )

    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_usage.total_tokens = 150
    mock_usage.prompt_tokens = 100
    mock_usage.completion_tokens = 50
    mock_response.usage = mock_usage

    return mock_response


@pytest.fixture
def mock_text_response():
    """Mock OpenAI API text response"""
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_usage = MagicMock()

    mock_message.content = "This is a test response from the LLM."
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_usage.total_tokens = 50
    mock_usage.prompt_tokens = 30
    mock_usage.completion_tokens = 20
    mock_response.usage = mock_usage

    return mock_response


class TestLLMClient:
    """Test LLMClient class"""

    def test_llm_client_initialization_with_api_key(self):
        """Test LLM client initialization with API key"""
        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None  # Test fallback to OPENAI_API_KEY
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_settings.OPENAI_BASE_URL = None  # No custom base URL

            with patch("app.llm.llm_client.OpenAI") as mock_openai:
                client = LLMClient()
                assert client.is_available()
                # When OPENAI_BASE_URL is None, base_url should not be passed
                mock_openai.assert_called_once_with(api_key="test-api-key")

    def test_llm_client_initialization_without_api_key(self):
        """Test LLM client initialization without API key"""
        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            client = LLMClient()
            assert not client.is_available()
            assert client.client is None

    def test_llm_client_initialization_with_openrouter_api_key(self):
        """Test LLM client initialization with OpenRouter API key (preferred)"""
        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "openai-key"
            mock_settings.OPENROUTER_API_KEY = "openrouter-key"  # This should be preferred
            mock_settings.OPENAI_MODEL = "gpt-4"
            mock_settings.OPENAI_BASE_URL = None

            with patch("app.llm.llm_client.OpenAI") as mock_openai:
                client = LLMClient()
                assert client.is_available()
                # OPENROUTER_API_KEY should be preferred over OPENAI_API_KEY
                mock_openai.assert_called_once_with(api_key="openrouter-key")

    def test_generate_structured_json_success(self, mock_openai_client, mock_openai_response):
        """Test successful structured JSON generation"""
        mock_openai_client.chat.completions.create.return_value = mock_openai_response

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()
                result = client.generate_structured_json(
                    prompt_id="evaluation",
                    variables={
                        "vin": "1HGBH41JXMN109186",
                        "make": "Honda",
                        "model": "Civic",
                        "year": 2019,
                        "mileage": 35000,
                        "condition": "excellent",
                        "asking_price": 22000,
                    },
                    response_model=DealEvaluation,
                )

                assert isinstance(result, DealEvaluation)
                assert result.fair_value == 24500.0
                assert result.score == 7.5
                assert len(result.insights) == 2
                assert len(result.talking_points) == 2

    def test_generate_structured_json_client_not_available(self):
        """Test structured JSON generation when client is not available"""
        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            mock_settings.OPENROUTER_API_KEY = None

            client = LLMClient()

            with pytest.raises(ApiError) as exc_info:
                client.generate_structured_json(
                    prompt_id="evaluation",
                    variables={},
                    response_model=DealEvaluation,
                )

            assert exc_info.value.status_code == 503
            assert "not available" in exc_info.value.message.lower()

    def test_generate_structured_json_invalid_prompt_id(self, mock_openai_client):
        """Test structured JSON generation with invalid prompt ID"""
        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_structured_json(
                        prompt_id="nonexistent_prompt",
                        variables={},
                        response_model=DealEvaluation,
                    )

                assert exc_info.value.status_code == 400
                assert "Invalid prompt_id" in exc_info.value.message

    def test_generate_structured_json_validation_error(
        self, mock_openai_client, mock_openai_response
    ):
        """Test structured JSON generation with validation error"""
        # Return invalid data that won't validate
        mock_openai_response.choices[0].message.content = json.dumps(
            {
                "fair_value": -1000,  # Invalid: negative value
                "score": 15.0,  # Invalid: out of range
                "insights": [],  # Invalid: empty list
                "talking_points": [],  # Invalid: empty list
            }
        )
        mock_openai_client.chat.completions.create.return_value = mock_openai_response

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_structured_json(
                        prompt_id="evaluation",
                        variables={
                            "vin": "1HGBH41JXMN109186",
                            "make": "Honda",
                            "model": "Civic",
                            "year": 2019,
                            "mileage": 35000,
                            "condition": "excellent",
                            "asking_price": 22000,
                        },
                        response_model=DealEvaluation,
                    )

                assert exc_info.value.status_code == 500
                assert "validation" in exc_info.value.message.lower()

    def test_generate_structured_json_openai_auth_error(self, mock_openai_client):
        """Test structured JSON generation with OpenAI authentication error"""
        mock_openai_client.chat.completions.create.side_effect = AuthenticationError(
            "Invalid API key", response=MagicMock(), body=None
        )

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "invalid-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_structured_json(
                        prompt_id="evaluation",
                        variables={
                            "vin": "1HGBH41JXMN109186",
                            "make": "Honda",
                            "model": "Civic",
                            "year": 2019,
                            "mileage": 35000,
                            "condition": "excellent",
                            "asking_price": 22000,
                        },
                        response_model=DealEvaluation,
                    )

                assert exc_info.value.status_code == 401
                assert "authentication" in exc_info.value.message.lower()

    def test_generate_structured_json_rate_limit_error(self, mock_openai_client):
        """Test structured JSON generation with rate limit error"""
        mock_openai_client.chat.completions.create.side_effect = RateLimitError(
            "Rate limit exceeded", response=MagicMock(), body=None
        )

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_structured_json(
                        prompt_id="evaluation",
                        variables={
                            "vin": "1HGBH41JXMN109186",
                            "make": "Honda",
                            "model": "Civic",
                            "year": 2019,
                            "mileage": 35000,
                            "condition": "excellent",
                            "asking_price": 22000,
                        },
                        response_model=DealEvaluation,
                    )

                assert exc_info.value.status_code == 429
                assert "rate limit" in exc_info.value.message.lower()

    def test_generate_structured_json_timeout_error(self, mock_openai_client):
        """Test structured JSON generation with timeout error"""
        mock_openai_client.chat.completions.create.side_effect = APITimeoutError(
            request=MagicMock()
        )

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_structured_json(
                        prompt_id="evaluation",
                        variables={
                            "vin": "1HGBH41JXMN109186",
                            "make": "Honda",
                            "model": "Civic",
                            "year": 2019,
                            "mileage": 35000,
                            "condition": "excellent",
                            "asking_price": 22000,
                        },
                        response_model=DealEvaluation,
                    )

                assert exc_info.value.status_code == 504
                assert "timed out" in exc_info.value.message.lower()

    def test_generate_structured_json_api_error(self, mock_openai_client):
        """Test structured JSON generation with general API error"""
        mock_openai_client.chat.completions.create.side_effect = APIError(
            "API Error", request=MagicMock(), body=None
        )

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_structured_json(
                        prompt_id="evaluation",
                        variables={
                            "vin": "1HGBH41JXMN109186",
                            "make": "Honda",
                            "model": "Civic",
                            "year": 2019,
                            "mileage": 35000,
                            "condition": "excellent",
                            "asking_price": 22000,
                        },
                        response_model=DealEvaluation,
                    )

                assert exc_info.value.status_code == 502

    def test_generate_structured_json_invalid_json_response(
        self, mock_openai_client, mock_openai_response
    ):
        """Test structured JSON generation with invalid JSON response"""
        mock_openai_response.choices[0].message.content = "This is not JSON at all"
        mock_openai_client.chat.completions.create.return_value = mock_openai_response

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_structured_json(
                        prompt_id="evaluation",
                        variables={
                            "vin": "1HGBH41JXMN109186",
                            "make": "Honda",
                            "model": "Civic",
                            "year": 2019,
                            "mileage": 35000,
                            "condition": "excellent",
                            "asking_price": 22000,
                        },
                        response_model=DealEvaluation,
                    )

                assert exc_info.value.status_code == 500
                assert "parse" in exc_info.value.message.lower()

    def test_generate_structured_json_empty_response(
        self, mock_openai_client, mock_openai_response
    ):
        """Test structured JSON generation with empty response"""
        mock_openai_response.choices[0].message.content = None
        mock_openai_client.chat.completions.create.return_value = mock_openai_response

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_structured_json(
                        prompt_id="evaluation",
                        variables={
                            "vin": "1HGBH41JXMN109186",
                            "make": "Honda",
                            "model": "Civic",
                            "year": 2019,
                            "mileage": 35000,
                            "condition": "excellent",
                            "asking_price": 22000,
                        },
                        response_model=DealEvaluation,
                    )

                # Empty response check happens before other processing
                assert exc_info.value.status_code == 500
                assert "empty response" in exc_info.value.message.lower()

    def test_generate_text_success(self, mock_openai_client, mock_text_response):
        """Test successful text generation"""
        mock_openai_client.chat.completions.create.return_value = mock_text_response

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()
                result = client.generate_text(
                    prompt_id="negotiation",
                    variables={
                        "make": "Honda",
                        "model": "Accord",
                        "year": 2020,
                        "asking_price": 25000,
                        "mileage": 45000,
                        "condition": "good",
                        "fair_value": 23500,
                        "score": 7.5,
                    },
                )

                assert isinstance(result, str)
                assert result == "This is a test response from the LLM."

    def test_generate_text_client_not_available(self):
        """Test text generation when client is not available"""
        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            mock_settings.OPENROUTER_API_KEY = None

            client = LLMClient()

            with pytest.raises(ApiError) as exc_info:
                client.generate_text(
                    prompt_id="negotiation",
                    variables={},
                )

            assert exc_info.value.status_code == 503
            assert "not available" in exc_info.value.message.lower()

    def test_generate_text_invalid_prompt_id(self, mock_openai_client):
        """Test text generation with invalid prompt ID"""
        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_text(
                        prompt_id="nonexistent_prompt",
                        variables={},
                    )

                assert exc_info.value.status_code == 400
                assert "Invalid prompt_id" in exc_info.value.message

    def test_generate_text_empty_response(self, mock_openai_client, mock_text_response):
        """Test text generation with empty response"""
        mock_text_response.choices[0].message.content = None
        mock_openai_client.chat.completions.create.return_value = mock_text_response

        with patch("app.llm.llm_client.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_API_KEY = None
            mock_settings.OPENAI_MODEL = "gpt-4"

            with patch("app.llm.llm_client.OpenAI", return_value=mock_openai_client):
                client = LLMClient()

                with pytest.raises(ApiError) as exc_info:
                    client.generate_text(
                        prompt_id="negotiation",
                        variables={
                            "make": "Honda",
                            "model": "Accord",
                            "year": 2020,
                            "asking_price": 25000,
                            "mileage": 45000,
                            "condition": "good",
                            "fair_value": 23500,
                            "score": 7.5,
                        },
                    )

                # Empty response check happens before other processing
                assert exc_info.value.status_code == 500
                assert "empty response" in exc_info.value.message.lower()
