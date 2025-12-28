"""
Agent Coordination and Data Integration Utilities

This module provides utilities for coordinating multi-agent workflows,
managing data flow between agents, and enriching context for better decision-making.

Key Concepts:
1. Agent Pipeline: Sequential execution of agents with context passing
2. Data Enrichment: Adding market data, historical context, and external API results
3. Context Management: Maintaining state across multi-step workflows
4. Agent Communication: Structured data passing between specialized agents
"""

import json
import logging
from typing import Any, Literal, TypeVar

from pydantic import BaseModel

# Import directly from llm_client to avoid circular import
# (since __init__.py imports from this module)
AgentRole = Literal["research", "loan", "negotiation", "evaluator", "qa"]

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class AgentContext(BaseModel):
    """
    Context object passed between agents in a multi-agent workflow

    This maintains state across agent executions and enables agents
    to build upon each other's work.
    """

    # User input and preferences
    user_criteria: dict[str, Any] = {}

    # Outputs from previous agents
    research_output: dict[str, Any] | None = None
    financing_output: dict[str, Any] | None = None
    negotiation_output: dict[str, Any] | None = None
    evaluation_output: dict[str, Any] | None = None
    qa_output: dict[str, Any] | None = None

    # External data enrichment
    market_data: dict[str, Any] = {}
    vehicle_history: dict[str, Any] = {}
    lender_recommendations: list[dict[str, Any]] = []

    # Workflow metadata
    current_step: str = "initial"
    errors: list[str] = []
    warnings: list[str] = []


class AgentPipeline:
    """
    Manages sequential execution of agents with context passing

    Example:
        pipeline = AgentPipeline()
        pipeline.add_step("research", research_agent_func)
        pipeline.add_step("financing", financing_agent_func)
        pipeline.add_step("negotiation", negotiation_agent_func)
        result = pipeline.execute(user_input)
    """

    def __init__(self):
        self.steps: list[tuple[str, callable]] = []
        self.context: AgentContext | None = None

    def add_step(self, step_name: str, agent_func: callable) -> "AgentPipeline":
        """
        Add an agent execution step to the pipeline

        Args:
            step_name: Name of the step (e.g., "research", "financing")
            agent_func: Function that takes AgentContext and returns result

        Returns:
            Self for method chaining
        """
        self.steps.append((step_name, agent_func))
        return self

    def execute(self, initial_context: dict[str, Any]) -> AgentContext:
        """
        Execute the agent pipeline with initial context

        Args:
            initial_context: User input and initial parameters

        Returns:
            Final AgentContext with all agent outputs
        """
        self.context = AgentContext(user_criteria=initial_context)

        for step_name, agent_func in self.steps:
            logger.info(f"Executing agent pipeline step: {step_name}")
            self.context.current_step = step_name

            try:
                result = agent_func(self.context)

                # Store result in appropriate context field
                if step_name == "research":
                    self.context.research_output = result
                elif step_name == "financing":
                    self.context.financing_output = result
                elif step_name == "negotiation":
                    self.context.negotiation_output = result
                elif (
                    step_name == "evaluation"
                    or step_name == "initial_evaluation"
                    or step_name == "final_evaluation"
                ):
                    self.context.evaluation_output = result
                elif step_name == "qa":
                    self.context.qa_output = result

                logger.info(f"Successfully completed step: {step_name}")

            except Exception as e:
                error_msg = f"Error in step {step_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.context.errors.append(error_msg)

        return self.context


class DataEnricher:
    """
    Utilities for enriching agent context with external data

    This class provides methods to integrate data from various sources
    into the agent workflow, making agents more context-aware.
    """

    @staticmethod
    def enrich_with_market_data(context: AgentContext, market_data: dict[str, Any]) -> AgentContext:
        """
        Add market intelligence data to context

        Args:
            context: Current agent context
            market_data: Market data from MarketCheck or similar APIs

        Returns:
            Enriched context
        """
        context.market_data = {
            **context.market_data,
            "pricing": market_data.get("pricing", {}),
            "inventory": market_data.get("inventory", {}),
            "trends": market_data.get("trends", {}),
            "comparables": market_data.get("comparables", []),
        }
        logger.info("Enriched context with market data")
        return context

    @staticmethod
    def enrich_with_vehicle_history(
        context: AgentContext, vehicle_history: dict[str, Any]
    ) -> AgentContext:
        """
        Add vehicle history report data to context

        Args:
            context: Current agent context
            vehicle_history: History data from CarFax/AutoCheck

        Returns:
            Enriched context
        """
        context.vehicle_history = {
            "title_status": vehicle_history.get("title_status", "Unknown"),
            "accident_history": vehicle_history.get("accidents", "Unknown"),
            "ownership_count": vehicle_history.get("owners", "Unknown"),
            "service_records": vehicle_history.get("service_records", "Unknown"),
            "odometer_readings": vehicle_history.get("odometer_history", []),
        }
        logger.info("Enriched context with vehicle history")
        return context

    @staticmethod
    def enrich_with_lender_recommendations(
        context: AgentContext, lender_data: list[dict[str, Any]]
    ) -> AgentContext:
        """
        Add lender recommendation data to context

        Args:
            context: Current agent context
            lender_data: Lender recommendations with match scores, APRs, features

        Returns:
            Enriched context
        """
        context.lender_recommendations = lender_data
        logger.info(f"Enriched context with {len(lender_data)} lender recommendations")
        return context

    @staticmethod
    def format_for_agent(
        context: AgentContext, agent_role: AgentRole, additional_vars: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Format context data for specific agent's prompt variables

        This method transforms the AgentContext into the variables
        expected by each agent's prompt template.

        Args:
            context: Current agent context
            agent_role: Target agent role
            additional_vars: Additional variables to merge

        Returns:
            Dictionary of prompt variables for the agent
        """
        base_vars = {}

        if agent_role == "research":
            # Research agent needs search criteria
            base_vars = {
                "make": context.user_criteria.get("make", ""),
                "model": context.user_criteria.get("model", ""),
                "price_min": context.user_criteria.get("price_min", ""),
                "price_max": context.user_criteria.get("price_max", ""),
                "condition": context.user_criteria.get("condition", ""),
                "year_min": context.user_criteria.get("year_min", ""),
                "year_max": context.user_criteria.get("year_max", ""),
                "mileage_max": context.user_criteria.get("mileage_max", ""),
                "location": context.user_criteria.get("location", ""),
            }

        elif agent_role == "loan":
            # Loan agent needs vehicle details and financial preferences
            base_vars = {
                "vehicle_report_json": json.dumps(context.research_output or {}),
                "loan_term_months": context.user_criteria.get("loan_term_months", 60),
                "down_payment": context.user_criteria.get("down_payment", 0),
                "interest_rate": context.user_criteria.get("interest_rate", 5.0),
                "credit_tier": context.user_criteria.get("credit_tier", "Good"),
                "monthly_budget": context.user_criteria.get("monthly_budget", ""),
                "annual_income": context.user_criteria.get("annual_income", ""),
                "lender_recommendations": (
                    json.dumps(context.lender_recommendations)
                    if context.lender_recommendations
                    else "Not available"
                ),
            }

        elif agent_role == "evaluator":
            # Evaluator needs research, financing outputs plus market and vehicle data
            # Note: Evaluator now runs BEFORE negotiation to provide price analysis
            base_vars = {
                "vehicle_report_json": json.dumps(context.research_output or {}),
                "financing_report_json": json.dumps(context.financing_output or {}),
                "fair_market_value": context.market_data.get("fair_market_value", 0),
                "vehicle_history_summary": context.vehicle_history.get("summary", "Unknown"),
                "safety_recalls_summary": context.market_data.get("recalls", "Unknown"),
                "days_on_market": context.market_data.get("days_on_market", "Unknown"),
                "sales_trends": json.dumps(context.market_data.get("trends", {})),
                "comparable_listings": json.dumps(context.market_data.get("comparables", [])),
                # For initial evaluation (before negotiation), provide asking price from research
                "asking_price": (
                    context.research_output.get("top_vehicles", [{}])[0].get("price", 0)
                    if context.research_output
                    else 0
                ),
            }

        elif agent_role == "negotiation":
            # Negotiation agent needs research, financing, and evaluation outputs plus market data
            # Evaluation output provides fair market value analysis for better negotiation
            base_vars = {
                "vehicle_report_json": json.dumps(context.research_output or {}),
                "financing_report_json": json.dumps(context.financing_output or {}),
                "evaluation_report": context.evaluation_output or "",
                "days_on_market": context.market_data.get("days_on_market", "Unknown"),
                "fair_market_price": context.market_data.get("fair_market_value", 0),
                "sales_stats": json.dumps(context.market_data.get("sales_stats", {})),
                "inventory_pressure": context.market_data.get("inventory_pressure", "Unknown"),
            }

        elif agent_role == "qa":
            # QA agent needs the final evaluation report (after negotiation) and all structured data
            base_vars = {
                "deal_evaluation_report": context.evaluation_output or "",
                "vehicle_report_json": json.dumps(context.research_output or {}),
                "financing_report_json": json.dumps(context.financing_output or {}),
                "negotiated_deal_json": json.dumps(context.negotiation_output or {}),
                "initial_evaluation": context.market_data.get("initial_evaluation", ""),
            }

        # Merge additional variables
        if additional_vars:
            base_vars.update(additional_vars)

        return base_vars


def create_vehicle_research_pipeline() -> AgentPipeline:
    """
    Create a standard vehicle research and evaluation pipeline

    This is a convenience function for the most common workflow:
    Research → Financing → Evaluation (Initial) → Negotiation → Evaluation (Final) → QA

    The evaluation step now runs BEFORE negotiation to provide:
    - Fair market value analysis from MarketCheck API
    - Price validation and recommendations
    - Risk assessment

    This information is then used by the negotiation agent to make better offers.

    Returns:
        Configured AgentPipeline
    """
    from app.llm import generate_structured_json, generate_text
    from app.llm.schemas import (
        FinancingReport,
        NegotiatedDeal,
        QAReport,
        VehicleReport,
    )

    pipeline = AgentPipeline()

    def research_step(context: AgentContext) -> dict[str, Any]:
        """Execute research agent"""
        variables = DataEnricher.format_for_agent(context, "research")
        result = generate_structured_json(
            prompt_id="research_vehicles",
            variables=variables,
            response_model=VehicleReport,
            agent_role="research",
            temperature=0.7,
        )
        return result.model_dump()

    def financing_step(context: AgentContext) -> dict[str, Any]:
        """Execute financing agent"""
        variables = DataEnricher.format_for_agent(context, "loan")
        result = generate_structured_json(
            prompt_id="analyze_financing",
            variables=variables,
            response_model=FinancingReport,
            agent_role="loan",
            temperature=0.7,
        )
        return result.model_dump()

    def initial_evaluation_step(context: AgentContext) -> str:
        """Execute initial evaluation agent (before negotiation)"""
        variables = DataEnricher.format_for_agent(context, "evaluator")
        result = generate_text(
            prompt_id="evaluate_deal",
            variables=variables,
            agent_role="evaluator",
            temperature=0.6,
        )
        # Store initial evaluation in market_data for later reference
        if not context.market_data:
            context.market_data = {}
        context.market_data["initial_evaluation"] = result
        return result

    def negotiation_step(context: AgentContext) -> dict[str, Any]:
        """Execute negotiation agent (uses evaluation output)"""
        variables = DataEnricher.format_for_agent(context, "negotiation")
        result = generate_structured_json(
            prompt_id="negotiate_deal",
            variables=variables,
            response_model=NegotiatedDeal,
            agent_role="negotiation",
            temperature=0.8,
        )
        return result.model_dump()

    def final_evaluation_step(context: AgentContext) -> str:
        """Execute final evaluation agent (after negotiation)"""
        variables = DataEnricher.format_for_agent(context, "evaluator")
        result = generate_text(
            prompt_id="evaluate_deal",
            variables=variables,
            agent_role="evaluator",
            temperature=0.6,
        )
        return result

    def qa_step(context: AgentContext) -> dict[str, Any]:
        """Execute QA agent"""
        variables = DataEnricher.format_for_agent(context, "qa")
        result = generate_structured_json(
            prompt_id="review_final_report",
            variables=variables,
            response_model=QAReport,
            agent_role="qa",
            temperature=0.5,
        )
        return result.model_dump()

    pipeline.add_step("research", research_step)
    pipeline.add_step("financing", financing_step)
    pipeline.add_step("initial_evaluation", initial_evaluation_step)
    pipeline.add_step("negotiation", negotiation_step)
    pipeline.add_step("evaluation", final_evaluation_step)
    pipeline.add_step("qa", qa_step)

    return pipeline


# Export public interface
__all__ = [
    "AgentContext",
    "AgentPipeline",
    "DataEnricher",
    "create_vehicle_research_pipeline",
]
