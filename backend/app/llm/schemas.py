"""
Pydantic schemas for LLM request/response validation
"""

from typing import Any

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    """Schema for LLM generation requests"""

    prompt_id: str = Field(..., description="ID of the prompt template to use")
    variables: dict[str, Any] = Field(
        default_factory=dict, description="Variables to substitute in the prompt template"
    )
    model: str | None = Field(None, description="Override the default OpenAI model")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature (0-2)"
    )
    max_tokens: int | None = Field(None, gt=0, description="Maximum number of tokens to generate")


class LLMResponse(BaseModel):
    """Schema for LLM generation responses"""

    content: str | dict[str, Any] = Field(..., description="Generated content")
    prompt_id: str = Field(..., description="ID of the prompt template used")
    model: str = Field(..., description="OpenAI model used for generation")
    tokens_used: int | None = Field(None, description="Total tokens used in the request")


class LLMError(BaseModel):
    """Schema for LLM error responses"""

    error_type: str = Field(
        ..., description="Type of error (e.g., 'api_error', 'validation_error')"
    )
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")

class CarSelectionItem(BaseModel):
    """Schema for a selected car from a list"""

    index: int = Field(..., description="Index of the vehicle in the provided list")
    score: float = Field(..., description="Confidence score (1-10)")
    highlights: list[str] = Field(..., description="Top 3 reasons to consider this vehicle")
    summary: str = Field(..., description="Brief recommendation summary")


class CarSelectionResponse(BaseModel):
    """Schema for car selection response"""

    recommendations: list[CarSelectionItem] = Field(
        ..., description="List of selected vehicles"
    )