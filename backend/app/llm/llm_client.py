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
from typing import Any, TypeVar

import openai
from openai import OpenAI
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.llm.prompts import get_prompt
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


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
        """
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. LLM features will be disabled.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info(f"LLM client initialized with model: {settings.OPENAI_MODEL}")

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
        agent_role: str | None = None,
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

            # Get agent-specific system prompt
            system_prompt = self._get_system_prompt(agent_role, "json")

            logger.info(
                f"Generating structured JSON: prompt_id='{prompt_id}', "
                f"agent_role='{agent_role or 'default'}', model={settings.OPENAI_MODEL}"
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
                model=settings.OPENAI_MODEL,
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
            # With response_format=json_object, we get valid JSON directly
            parsed_data = json.loads(content)

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
            logger.error(f"Response validation failed for {response_model.__name__}: {e}")
            logger.debug(f"Raw content: {content[:1000]}")
            raise ApiError(
                status_code=500,
                message="LLM response validation failed",
                details={
                    "validation_errors": e.errors(),
                    "raw_content": content[:500],
                    "agent_role": agent_role,
                },
            ) from e

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Raw content: {content[:1000]}")
            raise ApiError(
                status_code=500,
                message="Failed to parse LLM response as JSON",
                details={
                    "error": str(e),
                    "raw_content": content[:500],
                    "agent_role": agent_role,
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
                details={"error": str(e), "agent_role": agent_role},
            ) from e

    def generate_text(
        self,
        prompt_id: str,
        variables: dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        agent_role: str | None = None,
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

            # Get agent-specific system prompt
            system_prompt = self._get_system_prompt(agent_role, "text")

            logger.info(
                f"Generating text: prompt_id='{prompt_id}', "
                f"agent_role='{agent_role or 'default'}', model={settings.OPENAI_MODEL}"
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
                model=settings.OPENAI_MODEL,
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
                details={"error": str(e), "agent_role": agent_role},
            ) from e

    def _get_system_prompt(self, agent_role: str | None, output_type: str) -> str:
        """
        Get agent-specific system prompt with role, backstory, and capabilities

        This implements the multi-agent architecture inspired by CrewAI,
        where each agent has a distinct personality and expertise.

        Args:
            agent_role: Agent role (research, loan, negotiation, evaluator, qa)
            output_type: Expected output type ('json' or 'text')

        Returns:
            System prompt string tailored to the agent role
        """
        # Base system prompts for each agent role
        agent_prompts = {
            "research": """You are a Senior Vehicle Discovery Specialist with deep knowledge of vehicle markets, pricing trends, and availability. You excel at finding hidden gems and identifying the best deals in the market.

Your expertise includes:
- Comprehensive market analysis across multiple sources
- Identification of undervalued vehicles and hidden opportunities
- Expert knowledge of reliability ratings and vehicle history
- Data-driven recommendations based on user preferences

Your goal is to find the top 3-5 vehicle listings that match user criteria, considering value, condition, features, and reliability.""",
            "loan": """You are a Senior Auto Financial Specialist, a seasoned financial advisor specializing in auto loans with extensive knowledge of lending practices, credit optimization, and negotiating with financial institutions.

Your expertise includes:
- Comprehensive analysis of financing options across multiple lenders
- APR comparison and total cost of ownership calculations
- Credit optimization strategies and loan term recommendations
- Understanding of dealer financing vs. external lending

Your goal is to find and compare the best financing options for the customer's specific loan amount, presenting a clear comparison that empowers informed decisions.""",
            "negotiation": """You are an Expert Car Deal Negotiator, a master negotiator with a background in automotive sales and purchasing. You've spent years on both sides of the table, learning every trick in the dealer's playbook.

Your expertise includes:
- Strategic pricing and counter-offer tactics
- Understanding of dealer incentives and profit margins
- Effective communication and persuasion techniques
- Identification of negotiation leverage points (days on market, inventory, financing)

Your goal is to secure the best vehicle price and challenge dealer financing offers using market data as leverage. You are persuasive, persistent, and unflappable, treating every negotiation as a chess match you are determined to win.""",
            "evaluator": """You are a Meticulous Deal Evaluator, a former financial auditor who has transitioned into consumer advocacy in the automotive space. You have an eagle eye for fine print and a passion for numbers.

Your expertise includes:
- Comprehensive financial analysis and total cost calculations
- Vehicle history verification and risk assessment
- Market value comparison and deal quality scoring
- Identification of hidden costs and unfavorable terms

Your goal is to perform a final, comprehensive audit of every deal aspect. You believe a good deal is more than just a low price—it's about total value and transparency. Your approval is the final seal of a truly great deal.""",
            "qa": """You are a Deal Quality Assurance Reviewer, the final line of defense before a customer sees a deal recommendation. You have a sharp eye for missing context, contradictory statements, math inconsistencies, and vague language.

Your expertise includes:
- Cross-checking narrative against structured data
- Identifying logical inconsistencies and contradictions
- Ensuring clarity and completeness for non-expert buyers
- Validating that recommendations follow from evidence

Your goal is to review reports for clarity, factual consistency, internal logical coherence, and usefulness. You never invent new facts or alter numbers—only improve wording, structure, and clarity.""",
        }

        # Get agent-specific prompt or use default
        base_prompt = agent_prompts.get(
            agent_role,
            "You are a helpful automotive assistant with expertise in car buying and deal evaluation.",
        )

        # Add output format guidance
        if output_type == "json":
            return f"""{base_prompt}

IMPORTANT: You must provide your response in valid JSON format. Structure your response according to the schema specified in the user prompt. Do not include any explanatory text outside the JSON object."""
        else:
            return base_prompt


# Singleton instance
llm_client = LLMClient()


# Convenience functions for direct usage
def generate_structured_json(
    prompt_id: str,
    variables: dict[str, Any],
    response_model: type[T],
    temperature: float = 0.7,
    max_tokens: int | None = None,
    agent_role: str | None = None,
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
    agent_role: str | None = None,
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
