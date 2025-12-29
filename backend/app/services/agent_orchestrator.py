"""
Agent Orchestrator Service

Coordinates multiple specialized agents for complex tasks such as comprehensive
deal negotiations. This orchestrator implements a sequential agent pipeline where
each agent builds upon the work of previous agents.

Architecture:
1. Research Agent: Analyzes vehicle value and market data
2. Evaluator Agent: Assesses deal quality and fair pricing
3. Loan Agent: Calculates financing options and affordability
4. Negotiation Agent: Generates negotiation strategy
5. QA Agent: Reviews and validates final recommendation
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.llm import generate_structured_json
from app.llm.schemas import (
    DealEvaluation,
    FinancingReport,
    NegotiatedDeal,
    QAReport,
    VehicleReport,
)
from app.models.models import Deal
from app.repositories.deal_repository import DealRepository
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Coordinates multiple agents for complex tasks"""

    def __init__(self, db: Session):
        self.db = db
        self.deal_repo = DealRepository(db)

    async def negotiate_deal(self, deal_id: int, user_context: dict[str, Any]) -> dict[str, Any]:
        """
        Orchestrate a comprehensive deal negotiation using all specialized agents

        This method coordinates a multi-agent workflow:
        1. Research agent: Analyzes vehicle value
        2. Evaluator agent: Assesses deal quality
        3. Loan agent: Calculates financing options
        4. Negotiation agent: Generates strategy
        5. QA agent: Reviews final recommendation

        Args:
            deal_id: ID of the deal to negotiate
            user_context: User preferences and constraints
                - target_price: User's target price (optional)
                - down_payment: Down payment amount (optional)
                - monthly_budget: Monthly payment budget (optional)
                - loan_term_months: Desired loan term (optional)
                - credit_tier: Credit score tier (optional)
                - priorities: User's negotiation priorities (optional)

        Returns:
            Dictionary with comprehensive negotiation strategy including:
                - research: Vehicle analysis
                - evaluation: Deal quality assessment
                - financing: Loan options
                - negotiation: Strategy and talking points
                - qa_validation: Quality review
                - overall_recommendation: Go/No-Go decision

        Raises:
            ApiError: If deal not found or agent execution fails
        """
        logger.info(f"Starting orchestrated negotiation for deal {deal_id}")

        # Get deal details
        deal = self.deal_repo.get(deal_id)
        if not deal:
            raise ApiError(status_code=404, message=f"Deal with id {deal_id} not found")

        result: dict[str, Any] = {
            "deal_id": deal_id,
            "orchestration_steps": [],
        }

        try:
            # Step 1: Research Agent - Analyze vehicle value
            logger.info(f"[Deal {deal_id}] Step 1: Research agent analyzing vehicle")
            research_output = await self._research_vehicle(deal, user_context)
            result["research"] = research_output
            result["orchestration_steps"].append(
                {"step": "research", "status": "completed", "agent": "research"}
            )

        except Exception as e:
            logger.error(f"[Deal {deal_id}] Research agent failed: {str(e)}")
            result["orchestration_steps"].append(
                {
                    "step": "research",
                    "status": "failed",
                    "agent": "research",
                    "error": str(e),
                }
            )
            result["research"] = self._fallback_research(deal)

        try:
            # Step 2: Evaluator Agent - Assess deal quality
            logger.info(f"[Deal {deal_id}] Step 2: Evaluator agent assessing deal quality")
            evaluation_output = await self._evaluate_deal(
                deal, result.get("research"), user_context
            )
            result["evaluation"] = evaluation_output
            result["orchestration_steps"].append(
                {"step": "evaluation", "status": "completed", "agent": "evaluator"}
            )

        except Exception as e:
            logger.error(f"[Deal {deal_id}] Evaluator agent failed: {str(e)}")
            result["orchestration_steps"].append(
                {
                    "step": "evaluation",
                    "status": "failed",
                    "agent": "evaluator",
                    "error": str(e),
                }
            )
            result["evaluation"] = self._fallback_evaluation(deal)

        try:
            # Step 3: Loan Agent - Calculate financing options
            logger.info(f"[Deal {deal_id}] Step 3: Loan agent calculating financing")
            financing_output = await self._analyze_financing(deal, user_context)
            result["financing"] = financing_output
            result["orchestration_steps"].append(
                {"step": "financing", "status": "completed", "agent": "loan"}
            )

        except Exception as e:
            logger.error(f"[Deal {deal_id}] Loan agent failed: {str(e)}")
            result["orchestration_steps"].append(
                {"step": "financing", "status": "failed", "agent": "loan", "error": str(e)}
            )
            result["financing"] = self._fallback_financing(deal, user_context)

        try:
            # Step 4: Negotiation Agent - Generate strategy
            logger.info(f"[Deal {deal_id}] Step 4: Negotiation agent generating strategy")
            negotiation_output = await self._generate_negotiation_strategy(
                deal,
                result.get("research"),
                result.get("evaluation"),
                result.get("financing"),
                user_context,
            )
            result["negotiation"] = negotiation_output
            result["orchestration_steps"].append(
                {"step": "negotiation", "status": "completed", "agent": "negotiation"}
            )

        except Exception as e:
            logger.error(f"[Deal {deal_id}] Negotiation agent failed: {str(e)}")
            result["orchestration_steps"].append(
                {
                    "step": "negotiation",
                    "status": "failed",
                    "agent": "negotiation",
                    "error": str(e),
                }
            )
            result["negotiation"] = self._fallback_negotiation(
                deal, result.get("evaluation"), user_context
            )

        try:
            # Step 5: QA Agent - Review final recommendation
            logger.info(f"[Deal {deal_id}] Step 5: QA agent reviewing recommendation")
            qa_output = await self._qa_review(
                deal,
                result.get("research"),
                result.get("evaluation"),
                result.get("financing"),
                result.get("negotiation"),
            )
            result["qa_validation"] = qa_output
            result["orchestration_steps"].append(
                {"step": "qa_validation", "status": "completed", "agent": "qa"}
            )

        except Exception as e:
            logger.error(f"[Deal {deal_id}] QA agent failed: {str(e)}")
            result["orchestration_steps"].append(
                {"step": "qa_validation", "status": "failed", "agent": "qa", "error": str(e)}
            )
            result["qa_validation"] = {"is_valid": True, "issues": [str(e)]}

        # Generate overall recommendation
        result["overall_recommendation"] = self._generate_overall_recommendation(result)

        logger.info(
            f"[Deal {deal_id}] Orchestration completed. "
            f"Recommendation: {result['overall_recommendation']['decision']}"
        )
        return result

    async def _research_vehicle(self, deal: Deal, user_context: dict[str, Any]) -> dict[str, Any]:
        """Execute research agent to analyze vehicle value"""
        try:
            research_result = generate_structured_json(
                prompt_id="research_vehicles",
                variables={
                    "make": deal.vehicle_make or "Unknown",
                    "model": deal.vehicle_model or "Unknown",
                    "year": str(deal.vehicle_year) if deal.vehicle_year else "Unknown",
                    "mileage": deal.vehicle_mileage or 0,
                    "price_max": deal.asking_price,
                    "condition": "used",
                },
                response_model=VehicleReport,
                agent_role="research",
                temperature=0.7,
            )
            return research_result.model_dump()
        except Exception as e:
            logger.error(f"Research agent LLM call failed: {str(e)}")
            raise

    async def _evaluate_deal(
        self, deal: Deal, research_data: dict[str, Any] | None, user_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute evaluator agent to assess deal quality"""
        try:
            evaluation_result = generate_structured_json(
                prompt_id="evaluation",
                variables={
                    "vin": deal.vin or "Unknown",
                    "make": deal.vehicle_make or "Unknown",
                    "model": deal.vehicle_model or "Unknown",
                    "year": str(deal.vehicle_year) if deal.vehicle_year else "Unknown",
                    "asking_price": deal.asking_price,
                    "mileage": deal.vehicle_mileage or 0,
                    "condition": "used",
                },
                response_model=DealEvaluation,
                agent_role="evaluator",
                temperature=0.7,
            )
            return evaluation_result.model_dump()
        except Exception as e:
            logger.error(f"Evaluator agent LLM call failed: {str(e)}")
            raise

    async def _analyze_financing(self, deal: Deal, user_context: dict[str, Any]) -> dict[str, Any]:
        """Execute loan agent to calculate financing options"""
        try:
            financing_result = generate_structured_json(
                prompt_id="analyze_financing",
                variables={
                    "vehicle_report_json": "{}",  # Can be enriched with research data
                    "loan_term_months": user_context.get("loan_term_months", 60),
                    "down_payment": user_context.get("down_payment", deal.asking_price * 0.2),
                    "interest_rate": 5.0,  # Default rate
                    "credit_tier": user_context.get("credit_tier", "Good"),
                    "monthly_budget": user_context.get("monthly_budget", ""),
                    "annual_income": user_context.get("annual_income", ""),
                    "lender_recommendations": "Not available",
                },
                response_model=FinancingReport,
                agent_role="loan",
                temperature=0.7,
            )
            return financing_result.model_dump()
        except Exception as e:
            logger.error(f"Loan agent LLM call failed: {str(e)}")
            raise

    async def _generate_negotiation_strategy(
        self,
        deal: Deal,
        research_data: dict[str, Any] | None,
        evaluation_data: dict[str, Any] | None,
        financing_data: dict[str, Any] | None,
        user_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute negotiation agent to generate strategy"""
        try:
            # Prepare evaluation context
            fair_value = (
                evaluation_data.get("fair_value", deal.asking_price)
                if evaluation_data
                else deal.asking_price
            )
            eval_score = evaluation_data.get("score", 5.0) if evaluation_data else 5.0

            negotiation_result = generate_structured_json(
                prompt_id="negotiate_deal",
                variables={
                    "vehicle_report_json": str(research_data or {}),
                    "financing_report_json": str(financing_data or {}),
                    "evaluation_report": f"Fair Value: ${fair_value:,.2f}, Score: {eval_score}/10",
                    "days_on_market": "Unknown",
                    "fair_market_price": fair_value,
                    "sales_stats": "{}",
                    "inventory_pressure": "Unknown",
                },
                response_model=NegotiatedDeal,
                agent_role="negotiation",
                temperature=0.8,
            )
            return negotiation_result.model_dump()
        except Exception as e:
            logger.error(f"Negotiation agent LLM call failed: {str(e)}")
            raise

    async def _qa_review(
        self,
        deal: Deal,
        research_data: dict[str, Any] | None,
        evaluation_data: dict[str, Any] | None,
        financing_data: dict[str, Any] | None,
        negotiation_data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Execute QA agent to review final recommendation"""
        try:
            # Create a summary report for QA review
            evaluation_report = f"""
# Deal Evaluation Summary

**Vehicle**: {deal.vehicle_year} {deal.vehicle_make} {deal.vehicle_model}
**Asking Price**: ${deal.asking_price:,.2f}

## Evaluation Results
- Fair Value: ${evaluation_data.get('fair_value', 0):,.2f} (if evaluation_data else N/A)
- Score: {evaluation_data.get('score', 0)}/10 (if evaluation_data else N/A)

## Negotiation Strategy
- Target Price: ${negotiation_data.get('target_price', 0):,.2f} (if negotiation_data else N/A)
"""

            qa_result = generate_structured_json(
                prompt_id="review_final_report",
                variables={
                    "deal_evaluation_report": evaluation_report,
                    "vehicle_report_json": str(research_data or {}),
                    "financing_report_json": str(financing_data or {}),
                    "negotiated_deal_json": str(negotiation_data or {}),
                    "initial_evaluation": "",
                },
                response_model=QAReport,
                agent_role="qa",
                temperature=0.5,
            )
            return qa_result.model_dump()
        except Exception as e:
            logger.error(f"QA agent LLM call failed: {str(e)}")
            raise

    def _fallback_research(self, deal: Deal) -> dict[str, Any]:
        """Fallback research data when agent fails"""
        return {
            "top_vehicles": [
                {
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "price": deal.asking_price,
                    "mileage": deal.vehicle_mileage,
                }
            ],
            "market_summary": "Unable to fetch market data",
        }

    def _fallback_evaluation(self, deal: Deal) -> dict[str, Any]:
        """Fallback evaluation when agent fails"""
        return {
            "fair_value": deal.asking_price * 0.95,
            "score": 5.0,
            "insights": ["Unable to perform detailed evaluation"],
            "talking_points": [
                "Request vehicle history report",
                "Schedule pre-purchase inspection",
            ],
        }

    def _fallback_financing(self, deal: Deal, user_context: dict[str, Any]) -> dict[str, Any]:
        """Fallback financing when agent fails"""
        down_payment = user_context.get("down_payment", deal.asking_price * 0.2)
        loan_amount = deal.asking_price - down_payment
        monthly_payment = loan_amount / 60  # Simple 60-month calculation

        return {
            "recommended_option": {
                "lender_name": "Bank",
                "apr": 5.0,
                "loan_term_months": 60,
                "monthly_payment": round(monthly_payment, 2),
                "total_cost": round(deal.asking_price + (loan_amount * 0.15), 2),
            },
            "affordability_assessment": {
                "is_affordable": True,
                "notes": ["Unable to perform detailed affordability analysis"],
            },
        }

    def _fallback_negotiation(
        self, deal: Deal, evaluation_data: dict[str, Any] | None, user_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Fallback negotiation when agent fails"""
        fair_value = (
            evaluation_data.get("fair_value", deal.asking_price * 0.95)
            if evaluation_data
            else deal.asking_price * 0.95
        )
        target_price = user_context.get("target_price", fair_value)

        return {
            "target_price": round(target_price, 2),
            "opening_offer": round(target_price * 0.90, 2),
            "walk_away_price": round(target_price * 1.05, 2),
            "negotiation_summary": "Use fair market value as leverage. Be prepared to walk away if dealer won't negotiate.",
            "talking_points": [
                f"Reference fair market value of ${fair_value:,.2f}",
                "Request detailed vehicle history",
                "Ask about any available incentives or rebates",
            ],
        }

    def _generate_overall_recommendation(
        self, orchestration_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate final recommendation based on all agent outputs"""
        evaluation = orchestration_result.get("evaluation", {})
        qa_validation = orchestration_result.get("qa_validation", {})
        negotiation = orchestration_result.get("negotiation", {})

        # Determine decision based on evaluation score and QA validation
        score = evaluation.get("score", 0)
        is_valid = qa_validation.get("is_valid", False)
        issues = qa_validation.get("issues", [])

        if score >= 7.0 and is_valid and not issues:
            decision = "RECOMMEND"
            confidence = "High"
            summary = "This is a good deal. All agents recommend proceeding with negotiation."
        elif score >= 5.0 and is_valid:
            decision = "CONSIDER"
            confidence = "Medium"
            summary = "This deal has potential. Review the negotiation strategy carefully."
        else:
            decision = "NOT_RECOMMENDED"
            confidence = "Low"
            summary = "This deal has significant concerns. Consider alternative options."

        return {
            "decision": decision,
            "confidence": confidence,
            "summary": summary,
            "target_price": negotiation.get("target_price"),
            "next_steps": [
                "Review the detailed negotiation strategy",
                "Verify vehicle history and condition",
                "Consider financing options carefully",
            ],
        }


# Singleton instance
def get_agent_orchestrator(db: Session) -> AgentOrchestrator:
    """Factory function to create orchestrator with db session"""
    return AgentOrchestrator(db)
