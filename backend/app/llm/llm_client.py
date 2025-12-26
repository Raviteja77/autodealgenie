"""
Synchronous LLM client for OpenAI Chat Completions with Multi-Agent Intelligence

This module provides a centralized LLM client for the AutoDealGenie platform,
replacing CrewAI's heavy orchestration with direct OpenAI API integration.

Key Features:
- Synchronous OpenAI client for simpler deployment and debugging
- Multi-agent intelligence with role-based prompts and backstories
- Structured JSON output with Pydantic validation
- Comprehensive error handling with descriptive logging
- Support for agent-to-agent communication and context passing

Agent Architecture:
- Research Agent: Vehicle discovery and market analysis
- Loan Analyzer Agent: Financial options and lending recommendations
- Negotiation Agent: Deal negotiation strategies and tactics
- Deal Evaluator Agent: Comprehensive deal quality assessment
- Quality Assurance Agent: Final validation and review
"""

import json
import logging
from typing import Any, Literal, TypeVar

import openai
from openai import OpenAI
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.llm.agent_system_prompts import get_agent_system_prompt
from app.llm.prompts import get_prompt
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Valid agent roles
AgentRole = Literal["research", "loan", "negotiation", "evaluator", "qa"]


class LLMClient:
    """
    Synchronous client for OpenAI LLM operations with multi-agent intelligence

    This client supports modular, step-by-step agent operations that replace
    CrewAI's sequential orchestration with direct API calls. Each agent has
    a well-defined role, backstory, and set of capabilities.
    """

    def __init__(self):
        """
        Initialize the LLM client with OpenAI API key

        The client uses synchronous operations for simpler error handling
        and debugging compared to async alternatives.

        Supports custom base URLs for OpenRouter and other OpenAI-compatible endpoints.
        """
        if not hasattr(settings, "OPENROUTER_API_KEY") or not settings.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY not set. LLM features will be disabled.")
            self.client = None
        else:
            # Initialize with optional base_url for OpenRouter support
            client_kwargs = {"api_key": settings.OPENROUTER_API_KEY}
            # Determine base_url: check settings or default to OpenRouter
            base_url = getattr(settings, "OPENAI_API_BASE", None) or getattr(
                settings, "OPENAI_BASE_URL", None
            )

            if base_url:
                client_kwargs["base_url"] = base_url
                logger.info(f"LLM client initialized with custom endpoint: {base_url}")
            else:
                client_kwargs["base_url"] = "https://openrouter.ai/api/v1"

            self.client = OpenAI(**client_kwargs)
            logger.info(f"LLM client initialized with model: {settings.OPENAI_MODEL_NAME}")

    def is_available(self) -> bool:
        """
        Check if the LLM client is available and properly configured

        Returns:
            bool: True if client is initialized with valid API key
        """
        return self.client is not None

    def generate_structured_json(
        self,
        prompt_id: str,
        variables: dict[str, Any],
        response_model: type[T],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        agent_role: AgentRole | None = None,
    ) -> T:
        """
        Generate structured JSON output using OpenAI and validate with Pydantic model

        This method supports multi-agent workflows by allowing specification of
        agent roles (Research, Loan Analyzer, Negotiation, Evaluator, QA).
        The agent role influences the system prompt and response style.

        Args:
            prompt_id: ID of the prompt template to use (e.g., 'research_vehicles')
            variables: Variables to substitute in the prompt template
            response_model: Pydantic model class for response validation
            temperature: Sampling temperature (0.0-2.0). Lower for factual, higher for creative
            max_tokens: Maximum tokens to generate (optional)
            agent_role: Optional agent role for specialized system prompts

        Returns:
            Instance of response_model with validated data

        Raises:
            ApiError: If LLM is not available, prompt not found, or API call fails

        Example:
            >>> result = client.generate_structured_json(
            ...     prompt_id="research_vehicles",
            ...     variables={"make": "Honda", "model": "Civic"},
            ...     response_model=VehicleReport,
            ...     agent_role="research"
            ... )
        """
        if not self.is_available():
            logger.error("LLM client not available - OPENROUTER_API_KEY not configured")
            raise ApiError(
                status_code=503,
                message="LLM service is not available",
                details={"reason": "OPENROUTER_API_KEY not configured"},
            )

        try:
            # Get and format the prompt
            prompt_template = get_prompt(prompt_id)
            formatted_prompt = prompt_template.format(**variables)

            # Get agent-specific system prompt
            system_prompt = get_agent_system_prompt(agent_role, "json")

            logger.info(
                f"Generating structured JSON: prompt_id='{prompt_id}', "
                f"agent_role='{agent_role or 'default'}', model={settings.OPENAI_MODEL_NAME}"
            )

        except KeyError as e:
            logger.error(f"Prompt not found: {e}")
            raise ApiError(
                status_code=400,
                message=f"Invalid prompt_id: {prompt_id}",
                details={"error": str(e)},
            ) from e

        try:
            # Call OpenAI API with JSON mode
            # Using response_format to ensure valid JSON output
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": formatted_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )

            # Extract content from response
            content = response.choices[0].message.content
            if not content:
                logger.error("Empty response from OpenAI API")
                raise ApiError(
                    status_code=500,
                    message="Received empty response from LLM",
                    details={"prompt_id": prompt_id, "agent_role": agent_role},
                )

            # Log token usage for monitoring
            if response.usage:
                logger.info(
                    f"OpenAI tokens: {response.usage.total_tokens} "
                    f"(prompt: {response.usage.prompt_tokens}, "
                    f"completion: {response.usage.completion_tokens})"
                )

            # Parse JSON from response
            # First, check if the LLM returns Markdown code block and clean it
            if content.strip().startswith("```json") and content.strip().endswith("```"):
                logger.debug("Detected markdown code block in LLM response, cleaning it")
                content = content.strip()[7:-3].strip()
            elif content.strip().startswith("```") and content.strip().endswith("```"):
                logger.debug("Detected generic markdown code block in LLM response, cleaning it")
                # Handle ```\n{json}\n``` format
                content = content.strip()[3:-3].strip()

            # With response_format=json_object, we should get valid JSON directly
            # But we need to handle edge cases where the LLM may not comply perfectly
            try:
                parsed_data = json.loads(content)
            except json.JSONDecodeError as json_err:
                # Log the full raw content for debugging
                logger.error(
                    f"Initial JSON parsing failed. Error: {json_err}. "
                    f"Content length: {len(content)} characters"
                )
                logger.error(f"Raw content (first 1500 chars): {content[:1500]}")
                if len(content) > 1500:
                    logger.error(f"Raw content (last 500 chars): {content[-500:]}")
                # Re-raise to be caught by outer exception handler
                raise

            # Validate with Pydantic model
            validated_response = response_model.model_validate(parsed_data)
            logger.info(
                f"Successfully validated response with {response_model.__name__} "
                f"for agent_role='{agent_role or 'default'}'"
            )
            return validated_response

        except ApiError:
            # Re-raise ApiError without wrapping
            raise

        except ValidationError as e:
            logger.error(
                f"Response validation failed for {response_model.__name__}: {e}. "
                f"Content length: {len(content)} characters"
            )
            logger.error(f"Raw content (first 1500 chars): {content[:1500]}")
            if len(content) > 1500:
                logger.error(f"Raw content (last 500 chars): {content[-500:]}")
            logger.error(f"Validation errors: {e.errors()}")
            raise ApiError(
                status_code=500,
                message="LLM response validation failed",
                details={
                    "validation_errors": e.errors(),
                    "raw_content_preview": content[:500],
                    "content_length": len(content),
                    "agent_role": agent_role,
                    "prompt_id": prompt_id,
                },
            ) from e

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse JSON from LLM response: {e}. "
                f"Line: {e.lineno}, Column: {e.colno}, Position: {e.pos}. "
                f"Content length: {len(content)} characters"
            )
            logger.error(f"Raw content (first 1500 chars): {content[:1500]}")
            if len(content) > 1500:
                logger.error(f"Raw content (last 500 chars): {content[-500:]}")
            raise ApiError(
                status_code=500,
                message="Failed to parse LLM response as JSON",
                details={
                    "error": str(e),
                    "line": e.lineno,
                    "column": e.colno,
                    "position": e.pos,
                    "raw_content_preview": content[:500],
                    "content_length": len(content),
                    "agent_role": agent_role,
                    "prompt_id": prompt_id,
                },
            ) from e

        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise ApiError(
                status_code=401,
                message="OpenAI API authentication failed",
                details={"error": str(e)},
            ) from e

        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise ApiError(
                status_code=429,
                message="OpenAI API rate limit exceeded",
                details={
                    "error": str(e),
                    "retry_after": getattr(e, "retry_after", None),
                },
            ) from e

        except openai.APITimeoutError as e:
            logger.error(f"OpenAI API timeout: {e}")
            raise ApiError(
                status_code=504,
                message="OpenAI API request timed out",
                details={"error": str(e)},
            ) from e

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ApiError(
                status_code=502,
                message="OpenAI API error",
                details={
                    "error": str(e),
                    "status_code": getattr(e, "status_code", None),
                },
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error in generate_structured_json: {e}", exc_info=True)
            raise ApiError(
                status_code=500,
                message="Unexpected error during LLM generation",
                details={"error": str(e), "agent_role": agent_role},
            ) from e

    def generate_text(
        self,
        prompt_id: str,
        variables: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        agent_role: AgentRole | None = None,
    ) -> str:
        """
        Generate text output using OpenAI

        This method supports conversational and advisory responses from
        various agent roles in the multi-agent system.

        Args:
            prompt_id: ID of the prompt template to use
            variables: Variables to substitute in the prompt template
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate (optional)
            agent_role: Optional agent role for specialized system prompts

        Returns:
            Generated text string

        Raises:
            ApiError: If LLM is not available, prompt not found, or API call fails

        Example:
            >>> text = client.generate_text(
            ...     prompt_id="negotiation_advice",
            ...     variables={"price": 25000, "target": 23000},
            ...     agent_role="negotiation"
            ... )
        """
        if not self.is_available():
            logger.error("LLM client not available - OPENROUTER_API_KEY not configured")
            raise ApiError(
                status_code=503,
                message="LLM service is not available",
                details={"reason": "OPENROUTER_API_KEY not configured"},
            )

        try:
            # Get and format the prompt
            prompt_template = get_prompt(prompt_id)
            formatted_prompt = prompt_template.format(**variables)

            # Get agent-specific system prompt
            system_prompt = get_agent_system_prompt(agent_role, "text")

            logger.info(
                f"Generating text: prompt_id='{prompt_id}', "
                f"agent_role='{agent_role or 'default'}', model={settings.OPENAI_MODEL_NAME}"
            )

        except KeyError as e:
            logger.error(f"Prompt not found: {e}")
            raise ApiError(
                status_code=400,
                message=f"Invalid prompt_id: {prompt_id}",
                details={"error": str(e)},
            ) from e

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": formatted_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract content from response
            content = response.choices[0].message.content
            if not content:
                logger.error("Empty response from OpenAI API")
                raise ApiError(
                    status_code=500,
                    message="Received empty response from LLM",
                    details={"prompt_id": prompt_id, "agent_role": agent_role},
                )

            # Log token usage for monitoring
            if response.usage:
                logger.info(
                    f"OpenAI tokens: {response.usage.total_tokens} "
                    f"(prompt: {response.usage.prompt_tokens}, "
                    f"completion: {response.usage.completion_tokens})"
                )

            logger.info(
                f"Successfully generated text response ({len(content)} characters) "
                f"for agent_role='{agent_role or 'default'}'"
            )
            return content

        except ApiError:
            # Re-raise ApiError without wrapping
            raise

        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {e}")
            raise ApiError(
                status_code=401,
                message="OpenAI API authentication failed",
                details={"error": str(e)},
            ) from e

        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise ApiError(
                status_code=429,
                message="OpenAI API rate limit exceeded",
                details={
                    "error": str(e),
                    "retry_after": getattr(e, "retry_after", None),
                },
            ) from e

        except openai.APITimeoutError as e:
            logger.error(f"OpenAI API timeout: {e}")
            raise ApiError(
                status_code=504,
                message="OpenAI API request timed out",
                details={"error": str(e)},
            ) from e

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ApiError(
                status_code=502,
                message="OpenAI API error",
                details={
                    "error": str(e),
                    "status_code": getattr(e, "status_code", None),
                },
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error in generate_text: {e}", exc_info=True)
            raise ApiError(
                status_code=500,
                message="Unexpected error during LLM generation",
                details={"error": str(e), "agent_role": agent_role},
            ) from e


# Singleton instance
llm_client = LLMClient()


# Convenience functions for direct usage
def generate_structured_json(
    prompt_id: str,
    variables: dict[str, Any],
    response_model: type[T],
    temperature: float = 0.7,
    max_tokens: int | None = None,
    agent_role: AgentRole | None = None,
) -> T:
    """
    Generate structured JSON output using OpenAI and validate with Pydantic model

    This is a convenience wrapper around LLMClient.generate_structured_json()
    for direct module-level usage in service layers.

    Args:
        prompt_id: ID of the prompt template to use
        variables: Variables to substitute in the prompt template
        response_model: Pydantic model class for response validation
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate (optional)
        agent_role: Optional agent role for specialized system prompts

    Returns:
        Instance of response_model with validated data

    Raises:
        ApiError: If LLM is not available, prompt not found, or API call fails

    Example:
        >>> from app.llm import generate_structured_json
        >>> from app.llm.schemas import VehicleReport
        >>>
        >>> report = generate_structured_json(
        ...     prompt_id="research_vehicles",
        ...     variables={"make": "Honda", "budget": 25000},
        ...     response_model=VehicleReport,
        ...     agent_role="research"
        ... )
    """
    return llm_client.generate_structured_json(
        prompt_id=prompt_id,
        variables=variables,
        response_model=response_model,
        temperature=temperature,
        max_tokens=max_tokens,
        agent_role=agent_role,
    )


def generate_text(
    prompt_id: str,
    variables: dict[str, Any],
    temperature: float = 0.7,
    max_tokens: int | None = None,
    agent_role: AgentRole | None = None,
) -> str:
    """
    Generate text output using OpenAI

    This is a convenience wrapper around LLMClient.generate_text()
    for direct module-level usage in service layers.

    Args:
        prompt_id: ID of the prompt template to use
        variables: Variables to substitute in the prompt template
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate (optional)
        agent_role: Optional agent role for specialized system prompts

    Returns:
        Generated text string

    Raises:
        ApiError: If LLM is not available, prompt not found, or API call fails

    Example:
        >>> from app.llm import generate_text
        >>>
        >>> advice = generate_text(
        ...     prompt_id="negotiation_advice",
        ...     variables={"price": 25000, "target": 23000},
        ...     agent_role="negotiation"
        ... )
    """
    return llm_client.generate_text(
        prompt_id=prompt_id,
        variables=variables,
        temperature=temperature,
        max_tokens=max_tokens,
        agent_role=agent_role,
    )
