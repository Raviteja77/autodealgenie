"""
Asynchronous LLM client for OpenAI Chat Completions
"""

import json
import logging
from typing import Any, TypeVar

import openai
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.llm.prompts import get_prompt
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Asynchronous client for OpenAI LLM operations"""

    def __init__(self):
        """Initialize the LLM client with OpenAI API key"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. LLM features will be disabled.")
            self.client = None
        else:
            self.client = ChatOpenAI(api_key=settings.OPENAI_API_KEY)

    def is_available(self) -> bool:
        """Check if the LLM client is available"""
        return self.client is not None

    async def generate_structured_json(
        self,
        prompt_id: str,
        variables: dict[str, Any],
        response_model: type[T],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> T:
        """
        Generate structured JSON output using OpenAI and validate with Pydantic model

        Args:
            prompt_id: ID of the prompt template to use
            variables: Variables to substitute in the prompt template
            response_model: Pydantic model class for response validation
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate (optional)

        Returns:
            Instance of response_model with validated data

        Raises:
            ApiError: If LLM is not available, prompt not found, or API call fails
        """
        if not self.is_available():
            logger.error("LLM client not available - OPENAI_API_KEY not configured")
            raise ApiError(
                status_code=503,
                message="LLM service is not available",
                details={"reason": "OPENAI_API_KEY not configured"},
            )

        try:
            # Get and format the prompt
            prompt_template = get_prompt(prompt_id)
            formatted_prompt = prompt_template.format(**variables)
            logger.info(
                f"Generating structured JSON with prompt_id='{prompt_id}', "
                f"model={settings.OPENAI_MODEL}"
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
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides responses in valid JSON format.",
                    },
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
                    details={"prompt_id": prompt_id},
                )

            # Log token usage
            if response.usage:
                logger.info(
                    f"OpenAI API tokens used: {response.usage.total_tokens} "
                    f"(prompt: {response.usage.prompt_tokens}, "
                    f"completion: {response.usage.completion_tokens})"
                )

            # Parse JSON from response (handle markdown code blocks)
            json_content = self._extract_json(content)
            parsed_data = json.loads(json_content)

            # Validate with Pydantic model
            validated_response = response_model.model_validate(parsed_data)
            logger.info(f"Successfully validated response with {response_model.__name__}")
            return validated_response

        except ApiError:
            # Re-raise ApiError without wrapping
            raise

        except ValidationError as e:
            logger.error(f"Response validation failed: {e}")
            raise ApiError(
                status_code=500,
                message="LLM response validation failed",
                details={"validation_errors": e.errors(), "raw_content": content[:500]},
            ) from e

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Raw content: {content}")
            raise ApiError(
                status_code=500,
                message="Failed to parse LLM response as JSON",
                details={"error": str(e), "raw_content": content[:500]},
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
                details={"error": str(e), "retry_after": getattr(e, "retry_after", None)},
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
                details={"error": str(e), "status_code": getattr(e, "status_code", None)},
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error in generate_structured_json: {e}", exc_info=True)
            raise ApiError(
                status_code=500,
                message="Unexpected error during LLM generation",
                details={"error": str(e)},
            ) from e

    async def generate_text(
        self,
        prompt_id: str,
        variables: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate text output using OpenAI

        Args:
            prompt_id: ID of the prompt template to use
            variables: Variables to substitute in the prompt template
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate (optional)

        Returns:
            Generated text string

        Raises:
            ApiError: If LLM is not available, prompt not found, or API call fails
        """
        if not self.is_available():
            logger.error("LLM client not available - OPENAI_API_KEY not configured")
            raise ApiError(
                status_code=503,
                message="LLM service is not available",
                details={"reason": "OPENAI_API_KEY not configured"},
            )

        try:
            # Get and format the prompt
            prompt_template = get_prompt(prompt_id)
            formatted_prompt = prompt_template.format(**variables)
            logger.info(
                f"Generating text with prompt_id='{prompt_id}', model={settings.OPENAI_MODEL}"
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
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful automotive assistant."},
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
                    details={"prompt_id": prompt_id},
                )

            # Log token usage
            if response.usage:
                logger.info(
                    f"OpenAI API tokens used: {response.usage.total_tokens} "
                    f"(prompt: {response.usage.prompt_tokens}, "
                    f"completion: {response.usage.completion_tokens})"
                )

            logger.info(f"Successfully generated text response ({len(content)} characters)")
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
                details={"error": str(e), "retry_after": getattr(e, "retry_after", None)},
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
                details={"error": str(e), "status_code": getattr(e, "status_code", None)},
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error in generate_text: {e}", exc_info=True)
            raise ApiError(
                status_code=500,
                message="Unexpected error during LLM generation",
                details={"error": str(e)},
            ) from e

    def _extract_json(self, content: str) -> str:
        """
        Extract JSON from content, handling markdown code blocks

        Args:
            content: Raw content from LLM

        Returns:
            JSON string
        """
        # Handle markdown code blocks
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            if json_end != -1:
                return content[json_start:json_end].strip()
        elif "```" in content:
            json_start = content.find("```") + 3
            json_end = content.find("```", json_start)
            if json_end != -1:
                return content[json_start:json_end].strip()

        # Return content as-is if no code blocks found
        return content.strip()


# Singleton instance
llm_client = LLMClient()


# Convenience functions for direct usage
async def generate_structured_json(
    prompt_id: str,
    variables: dict[str, Any],
    response_model: type[T],
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> T:
    """
    Generate structured JSON output using OpenAI and validate with Pydantic model

    This is a convenience wrapper around LLMClient.generate_structured_json()

    Args:
        prompt_id: ID of the prompt template to use
        variables: Variables to substitute in the prompt template
        response_model: Pydantic model class for response validation
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate (optional)

    Returns:
        Instance of response_model with validated data

    Raises:
        ApiError: If LLM is not available, prompt not found, or API call fails
    """
    return await llm_client.generate_structured_json(
        prompt_id=prompt_id,
        variables=variables,
        response_model=response_model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


async def generate_text(
    prompt_id: str,
    variables: dict[str, Any],
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> str:
    """
    Generate text output using OpenAI

    This is a convenience wrapper around LLMClient.generate_text()

    Args:
        prompt_id: ID of the prompt template to use
        variables: Variables to substitute in the prompt template
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate (optional)

    Returns:
        Generated text string

    Raises:
        ApiError: If LLM is not available, prompt not found, or API call fails
    """
    return await llm_client.generate_text(
        prompt_id=prompt_id,
        variables=variables,
        temperature=temperature,
        max_tokens=max_tokens,
    )
