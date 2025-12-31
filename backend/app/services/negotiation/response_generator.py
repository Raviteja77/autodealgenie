import logging

from app.llm import generate_text

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Orchestrates LLM calls for various negotiation phases with specific agent roles."""

    @staticmethod
    async def generate_initial(variables: dict) -> str:
        """Initial negotiation strategy response."""
        return generate_text(
            prompt_id="negotiation_initial",
            variables=variables,
            agent_role="negotiation",
            temperature=0.7,
        )

    @staticmethod
    async def generate_counter(variables: dict) -> str:
        """Response to a dealer or user counter-offer."""
        return generate_text(
            prompt_id="negotiation_counter",
            variables=variables,
            agent_role="negotiation",
            temperature=0.7,
        )

    @staticmethod
    async def generate_chat(variables: dict) -> str:
        """General chat and Q&A response."""
        return generate_text(
            prompt_id="negotiation_chat",
            variables=variables,
            agent_role="negotiation",
            temperature=0.8,
        )

    @staticmethod
    async def generate_dealer_analysis(variables: dict) -> str:
        """Analysis of dealer info using the 'evaluator' agent role."""
        return generate_text(
            prompt_id="dealer_info_analysis",
            variables=variables,
            agent_role="evaluator",
            temperature=0.7,
        )
