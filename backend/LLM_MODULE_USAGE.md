# LLM Module Usage Guide

This document provides examples of how to use the LLM module in the AutoDealGenie backend.

## Overview

The LLM module provides an asynchronous interface to OpenAI's Chat Completions API with:
- Structured JSON generation with Pydantic validation
- Text generation
- Centralized prompt management
- Comprehensive error handling
- Structured logging

## Basic Usage

### 1. Importing the LLM Client

```python
from app.llm import generate_structured_json, generate_text
from app.llm.prompts import get_prompt
```

### 2. Generating Structured JSON

Use `generate_structured_json()` when you need the LLM to return data in a specific structure:

```python
from pydantic import BaseModel, Field
from app.llm import generate_structured_json

class CarRecommendation(BaseModel):
    """Model for car recommendation response"""
    make: str
    model: str
    year: int
    price_range: str
    key_features: list[str]
    why_recommended: str

# Generate structured response
recommendations = await generate_structured_json(
    prompt_id="car_recommendation",
    variables={
        "budget": 30000,
        "body_type": "SUV",
        "preferred_makes": "Honda, Toyota",
        "required_features": "AWD, Backup Camera",
        "usage_type": "Family vehicle",
    },
    response_model=CarRecommendation,
    temperature=0.7,
)

# Access validated data
print(f"Recommended: {recommendations.make} {recommendations.model}")
```

### 3. Generating Text

Use `generate_text()` for free-form text generation:

```python
from app.llm import generate_text

# Generate negotiation strategy
strategy = await generate_text(
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
    temperature=0.7,
)

print(strategy)
```

## Using in FastAPI Endpoints

### Example 1: Simple Endpoint

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.dependencies import get_current_user
from app.llm import generate_structured_json
from app.models.models import User

router = APIRouter()


class DealAnalysisRequest(BaseModel):
    """Request schema for deal analysis"""
    vehicle_vin: str = Field(..., min_length=17, max_length=17)
    asking_price: float = Field(..., gt=0)
    mileage: int = Field(..., ge=0)
    condition: str


class DealAnalysisResponse(BaseModel):
    """Response schema for deal analysis"""
    fair_value: float
    score: float
    insights: list[str]
    talking_points: list[str]


@router.post("/analyze", response_model=DealAnalysisResponse)
async def analyze_deal(
    request: DealAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze a car deal using AI"""
    result = await generate_structured_json(
        prompt_id="evaluation",
        variables={
            "vin": request.vehicle_vin,
            "make": "Honda",  # From VIN lookup or user input
            "model": "Civic",
            "year": 2020,
            "mileage": request.mileage,
            "condition": request.condition,
            "asking_price": request.asking_price,
        },
        response_model=DealAnalysisResponse,
    )
    return result
```

### Example 2: Service Layer Pattern

Create a service that uses the LLM module:

```python
# app/services/recommendation_service.py
import logging
from typing import Any

from pydantic import BaseModel

from app.llm import generate_structured_json, generate_text
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)


class VehicleRecommendation(BaseModel):
    """Vehicle recommendation model"""
    make: str
    model: str
    year: int
    price_range: str
    features: list[str]
    reasoning: str


class RecommendationService:
    """Service for generating vehicle recommendations"""

    async def get_recommendations(
        self,
        budget: float,
        preferences: dict[str, Any],
    ) -> list[VehicleRecommendation]:
        """
        Get vehicle recommendations based on user preferences

        Args:
            budget: User's budget
            preferences: Dict with body_type, features, usage, etc.

        Returns:
            List of vehicle recommendations

        Raises:
            ApiError: If LLM service fails
        """
        try:
            # Format preferences for prompt
            variables = {
                "budget": budget,
                "body_type": preferences.get("body_type", "Any"),
                "preferred_makes": ", ".join(preferences.get("makes", [])),
                "required_features": ", ".join(preferences.get("features", [])),
                "usage_type": preferences.get("usage", "General use"),
            }

            # Generate recommendations
            recommendations = await generate_structured_json(
                prompt_id="car_recommendation",
                variables=variables,
                response_model=VehicleRecommendation,
                temperature=0.7,
            )

            logger.info(f"Generated recommendations for budget ${budget}")
            return [recommendations]

        except ApiError:
            # Re-raise ApiError from LLM module
            raise

        except Exception as e:
            logger.error(f"Unexpected error in get_recommendations: {e}")
            raise ApiError(
                status_code=500,
                message="Failed to generate recommendations",
                details={"error": str(e)},
            )


# Singleton instance
recommendation_service = RecommendationService()
```

Then use the service in an endpoint:

```python
# app/api/v1/endpoints/recommendations.py
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.models import User
from app.services.recommendation_service import recommendation_service

router = APIRouter()


@router.post("/recommendations")
async def get_vehicle_recommendations(
    budget: float,
    preferences: dict,
    current_user: User = Depends(get_current_user),
):
    """Get AI-powered vehicle recommendations"""
    recommendations = await recommendation_service.get_recommendations(
        budget=budget,
        preferences=preferences,
    )
    return {"recommendations": recommendations}
```

## Available Prompts

The module includes the following pre-defined prompts:

1. **car_recommendation**: Generate vehicle recommendations based on user preferences
2. **negotiation**: Create negotiation strategies for vehicle purchases
3. **evaluation**: Evaluate deal quality with fair market value analysis
4. **deal_summary**: Generate concise deal summaries
5. **vehicle_comparison**: Compare two vehicles side-by-side

### Adding Custom Prompts

Add new prompts to `app/llm/prompts.py`:

```python
PROMPTS["custom_prompt"] = PromptTemplate(
    id="custom_prompt",
    template="""Your prompt template here with {variables}""",
)
```

## Error Handling

The LLM module uses the project's standard error handling conventions:

```python
from app.llm import generate_text
from app.utils.error_handler import ApiError

try:
    result = await generate_text(
        prompt_id="evaluation",
        variables={...},
    )
except ApiError as e:
    # Handle specific error cases
    if e.status_code == 401:
        # Authentication error
        logger.error("OpenAI API authentication failed")
    elif e.status_code == 429:
        # Rate limit error
        logger.warning("OpenAI rate limit exceeded")
    elif e.status_code == 503:
        # Service unavailable
        logger.error("LLM service not configured")
    
    # Re-raise or handle appropriately
    raise
```

## Configuration

The LLM module reads configuration from environment variables:

```env
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
```

Set these in your `.env` file or environment.

## Testing

When testing code that uses the LLM module, mock the OpenAI client:

```python
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

@pytest.mark.asyncio
async def test_my_endpoint():
    """Test endpoint that uses LLM"""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"result": "test"}'
    
    with patch("app.llm.llm_client.AsyncOpenAI") as mock_openai:
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test your code
        result = await my_function()
        assert result == expected_value
```

See `tests/llm/test_llm_client.py` for comprehensive examples.

## Best Practices

1. **Use Pydantic Models**: Always define response models for structured JSON generation
2. **Handle Errors**: Wrap LLM calls in try-except blocks and handle ApiError appropriately
3. **Log Operations**: The module logs automatically, but add context in your application code
4. **Monitor Token Usage**: Token usage is logged; monitor for cost control
5. **Use Appropriate Temperature**: Lower (0.2-0.5) for factual tasks, higher (0.7-1.0) for creative tasks
6. **Set Max Tokens**: Use `max_tokens` parameter to control response length and cost
7. **Cache Results**: Consider caching LLM responses for repeated queries
8. **Graceful Degradation**: Provide fallback behavior when LLM service is unavailable

## Performance Considerations

- **Async Operations**: All LLM operations are asynchronous; use `await` appropriately
- **Concurrent Requests**: Use `asyncio.gather()` for parallel LLM requests
- **Timeout Handling**: OpenAI API timeouts are handled automatically and return 504 errors
- **Rate Limiting**: Monitor for 429 errors and implement exponential backoff if needed

## Example: Concurrent Requests

```python
import asyncio
from app.llm import generate_text

async def analyze_multiple_vehicles(vehicles: list[dict]) -> list[str]:
    """Analyze multiple vehicles concurrently"""
    tasks = [
        generate_text(
            prompt_id="evaluation",
            variables=vehicle,
        )
        for vehicle in vehicles
    ]
    
    # Execute all requests concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle results and errors
    analyses = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Failed to analyze vehicle {i}: {result}")
            analyses.append("Analysis unavailable")
        else:
            analyses.append(result)
    
    return analyses
```

## Monitoring and Logging

The module logs the following events:

- **Info**: Successful operations, token usage
- **Warning**: Missing API key, service unavailable
- **Error**: API failures, validation errors, unexpected errors
- **Debug**: Raw LLM responses (for troubleshooting)

Monitor logs for patterns that indicate issues:
- Frequent authentication errors → Check API key
- Frequent rate limit errors → Implement rate limiting or upgrade plan
- Frequent validation errors → Review prompt templates and response models

## Migration from LangChain Service

If you're migrating from the existing `langchain_service.py`:

**Before:**
```python
from app.services.langchain_service import langchain_service

result = await langchain_service.analyze_vehicle_price(
    make="Honda",
    model="Accord",
    year=2020,
    mileage=45000,
    condition="good",
    asking_price=25000,
)
```

**After:**
```python
from app.llm import generate_structured_json
from pydantic import BaseModel

class VehicleAnalysis(BaseModel):
    fair_value: float
    assessment: str
    factors: list[str]

result = await generate_structured_json(
    prompt_id="evaluation",
    variables={
        "make": "Honda",
        "model": "Accord",
        "year": 2020,
        "mileage": 45000,
        "condition": "good",
        "asking_price": 25000,
    },
    response_model=VehicleAnalysis,
)
```

The new module provides better type safety, error handling, and testing capabilities.
