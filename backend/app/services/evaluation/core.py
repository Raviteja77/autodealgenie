"""
Deal Evaluation Service - Core Orchestrator

Provides fair market value analysis and negotiation insights for vehicle deals.
This orchestrator delegates to specialized evaluators following the pattern
established in the Negotiation Service.
"""

import hashlib
import json
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.evaluation_config import EvaluationConfig
from app.db.redis import redis_client
from app.models.evaluation import EvaluationStatus, PipelineStep
from app.models.models import Deal
from app.repositories.evaluation_repository import EvaluationRepository
from app.services.base_service import BaseService
from app.services.evaluation.condition import ConditionEvaluator
from app.services.evaluation.financing import FinancingEvaluator
from app.services.evaluation.pricing import PricingEvaluator
from app.services.evaluation.risk import RiskEvaluator

logger = logging.getLogger(__name__)


class DealEvaluationService(BaseService):
    """
    Orchestrates deal evaluation by delegating to specialized evaluator modules.

    This service coordinates:
    - ConditionEvaluator: Vehicle condition assessment
    - PricingEvaluator: Market pricing and value analysis
    - FinancingEvaluator: Affordability and financing metrics
    - RiskEvaluator: Risk factor analysis

    Inherits from BaseService for common database and error patterns.
    """

    def __init__(self, db: AsyncSession | None = None):
        """
        Initialize the orchestrator and all sub-modules.

        Args:
            db: Optional database session (for pipeline operations)
        """
        if db:
            super().__init__(db)
        else:
            self.db = None

        # Initialize all sub-modules
        self.condition_evaluator = ConditionEvaluator()
        self.pricing_evaluator = PricingEvaluator()
        self.financing_evaluator = FinancingEvaluator()
        self.risk_evaluator = RiskEvaluator()

    def _generate_cache_key(
        self,
        vehicle_vin: str,
        asking_price: float,
        condition: str,
        mileage: int,
        make: str | None = None,
        model: str | None = None,
        year: int | None = None,
    ) -> str:
        """
        Generate a unique cache key based on all evaluation-affecting parameters.

        Args:
            vehicle_vin: Vehicle Identification Number
            asking_price: Asking price in USD
            condition: Vehicle condition descriptor
            mileage: Vehicle mileage in miles
            make: Vehicle make (optional)
            model: Vehicle model (optional)
            year: Vehicle year (optional)

        Returns:
            Cache key string
        """
        key_payload: dict[str, Any] = {
            "vin": vehicle_vin,
            "asking_price": round(asking_price, 2),
            "condition": condition.lower(),
            "mileage": mileage,
        }
        if make is not None:
            key_payload["make"] = make.lower()
        if model is not None:
            key_payload["model"] = model.lower()
        if year is not None:
            key_payload["year"] = year

        key_data = json.dumps(key_payload, sort_keys=True, separators=(",", ":"))
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"{EvaluationConfig.CACHE_KEY_PREFIX}:{key_hash}"

    async def _get_cached_evaluation(self, cache_key: str) -> dict[str, Any] | None:
        """
        Retrieve cached evaluation result from Redis.

        Args:
            cache_key: Cache key to lookup

        Returns:
            Cached evaluation result or None if not found
        """
        try:
            redis = redis_client.get_client()
            if redis is None:
                logger.debug("Redis client not available, skipping cache lookup")
                return None

            cached_data = await redis.get(cache_key)
            if cached_data:
                logger.info(f"Cache HIT for key: {cache_key}")
                return json.loads(cached_data)
            else:
                logger.info(f"Cache MISS for key: {cache_key}")
                return None
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {e}")
            return None

    async def _set_cached_evaluation(self, cache_key: str, evaluation: dict[str, Any]) -> None:
        """
        Store evaluation result in Redis cache.

        Args:
            cache_key: Cache key to store under
            evaluation: Evaluation result to cache
        """
        try:
            redis = redis_client.get_client()
            if redis is None:
                logger.debug("Redis client not available, skipping cache set")
                return

            await redis.setex(
                cache_key, EvaluationConfig.CACHE_TTL, json.dumps(evaluation)
            )
            logger.info(
                f"Cached evaluation for key: {cache_key} (TTL: {EvaluationConfig.CACHE_TTL}s)"
            )
        except Exception as e:
            logger.warning(f"Error storing to cache: {e}")

    async def evaluate_deal(
        self,
        vehicle_vin: str,
        asking_price: float,
        condition: str,
        mileage: int,
        make: str | None = None,
        model: str | None = None,
        year: int | None = None,
        zip_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate a car deal and provide comprehensive analysis.

        This is the single source of truth for deal evaluation, orchestrating
        all sub-modules to produce a unified result.

        Args:
            vehicle_vin: 17-character Vehicle Identification Number
            asking_price: Asking price in USD
            condition: Vehicle condition description
            mileage: Current mileage in miles
            make: Vehicle make (optional)
            model: Vehicle model (optional)
            year: Vehicle year (optional)
            zip_code: Optional ZIP code for location-based pricing

        Returns:
            Dictionary containing fair_value, score, insights, and talking_points
        """
        logger.info(f"Evaluating deal for VIN: {vehicle_vin}, Price: ${asking_price:,.2f}")

        # Check cache
        cache_key = self._generate_cache_key(
            vehicle_vin, asking_price, condition, mileage, make, model, year
        )
        cached_result = await self._get_cached_evaluation(cache_key)

        if cached_result:
            logger.info(f"Returning cached evaluation for VIN: {vehicle_vin}")
            return cached_result

        # Delegate to pricing evaluator
        result = await self.pricing_evaluator.evaluate(
            vehicle_vin=vehicle_vin,
            asking_price=asking_price,
            condition=condition,
            mileage=mileage,
            make=make,
            model=model,
            year=year,
            zip_code=zip_code,
        )

        # Cache the result
        await self._set_cached_evaluation(cache_key, result)

        return result

    # Multi-step pipeline methods

    async def process_evaluation_step(
        self,
        db: AsyncSession,
        evaluation_id: int,
        user_answers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Process the current step of an evaluation pipeline.

        Args:
            db: Database session
            evaluation_id: Evaluation ID
            user_answers: Optional answers to previous questions

        Returns:
            Dictionary containing step result with either assessment or questions
        """
        repo = EvaluationRepository(db)
        evaluation = await repo.get(evaluation_id)

        if not evaluation:
            raise ValueError(f"Evaluation {evaluation_id} not found")

        # Get the deal details
        result = await db.execute(select(Deal).filter(Deal.id == evaluation.deal_id))
        deal = result.scalar_one_or_none()
        if not deal:
            raise ValueError(f"Deal {evaluation.deal_id} not found")

        current_step = evaluation.current_step
        result_json = evaluation.result_json or {}

        # Incorporate user answers
        if user_answers:
            result_json.setdefault("user_inputs", {}).update(user_answers)

        # Process based on current step
        if current_step == PipelineStep.VEHICLE_CONDITION:
            step_result = await self._evaluate_vehicle_condition(deal, result_json)
        elif current_step == PipelineStep.PRICE:
            step_result = await self._evaluate_price(deal, result_json)
        elif current_step == PipelineStep.FINANCING:
            step_result = await self._evaluate_financing(deal, result_json)
        elif current_step == PipelineStep.RISK:
            step_result = await self._evaluate_risk(deal, result_json)
        elif current_step == PipelineStep.FINAL:
            step_result = await self._evaluate_final(deal, result_json)
        else:
            raise ValueError(f"Unknown pipeline step: {current_step}")

        # Update evaluation
        if step_result.get("questions"):
            result_json[current_step.value] = step_result
            await repo.update_result(evaluation_id, result_json, EvaluationStatus.AWAITING_INPUT)
        else:
            result_json[current_step.value] = step_result
            next_step = self._get_next_step(current_step)

            if next_step:
                await repo.update_step(evaluation_id, next_step)
                await repo.update_result(evaluation_id, result_json, EvaluationStatus.ANALYZING)
            else:
                await repo.update_result(evaluation_id, result_json, EvaluationStatus.COMPLETED)

        return step_result

    def _get_next_step(self, current_step: PipelineStep) -> PipelineStep | None:
        """Get the next step in the pipeline."""
        step_order = [
            PipelineStep.VEHICLE_CONDITION,
            PipelineStep.PRICE,
            PipelineStep.FINANCING,
            PipelineStep.RISK,
            PipelineStep.FINAL,
        ]

        try:
            current_index = step_order.index(current_step)
            if current_index < len(step_order) - 1:
                return step_order[current_index + 1]
        except ValueError:
            pass

        return None

    async def _evaluate_vehicle_condition(self, deal: Deal, result_json: dict) -> dict[str, Any]:
        """Evaluate vehicle condition step using ConditionEvaluator."""
        user_inputs = result_json.get("user_inputs", {})

        # Check for required data
        required_fields = ["vin", "condition_description"]
        missing_fields = [f for f in required_fields if f not in user_inputs]

        if missing_fields:
            return {
                "questions": [
                    "What is the Vehicle Identification Number (VIN)?",
                    "Please describe the vehicle's condition (e.g., excellent, good, fair, poor)",
                ],
                "required_fields": required_fields,
            }

        # Delegate to ConditionEvaluator
        assessment = await self.condition_evaluator.evaluate(
            make=deal.vehicle_make or "Unknown",
            model=deal.vehicle_model or "Unknown",
            year=deal.vehicle_year,
            vin=user_inputs.get("vin", "Unknown"),
            mileage=deal.vehicle_mileage,
            condition_description=user_inputs.get("condition_description", "Not provided"),
        )

        return {"assessment": assessment, "completed": True}

    async def _evaluate_price(self, deal: Deal, result_json: dict) -> dict[str, Any]:
        """Evaluate price step using PricingEvaluator."""
        user_inputs = result_json.get("user_inputs", {})
        vin = user_inputs.get("vin", "UNKNOWN")
        condition = user_inputs.get("condition_description", "unknown")

        # Delegate to PricingEvaluator
        price_eval = await self.pricing_evaluator.evaluate(
            vehicle_vin=vin,
            asking_price=deal.asking_price,
            condition=condition,
            mileage=deal.vehicle_mileage,
            make=deal.vehicle_make,
            model=deal.vehicle_model,
            year=deal.vehicle_year,
        )

        return {
            "assessment": {
                "fair_value": price_eval["fair_value"],
                "score": price_eval["score"],
                "insights": price_eval["insights"],
                "talking_points": price_eval["talking_points"],
            },
            "completed": True,
        }

    async def _evaluate_financing(self, deal: Deal, result_json: dict) -> dict[str, Any]:
        """Evaluate financing step using FinancingEvaluator."""
        user_inputs = result_json.get("user_inputs", {})

        # Check if financing information is provided
        if "financing_type" not in user_inputs:
            return {
                "questions": [
                    "What type of financing are you considering? (cash, loan, lease)",
                    "If financing, what is your estimated interest rate? (optional)",
                    "What is your planned down payment amount? (optional)",
                    "What is your approximate monthly gross income? (optional, for affordability check)",
                ],
                "required_fields": ["financing_type"],
            }

        financing_type = user_inputs.get("financing_type", "").lower()
        monthly_income = user_inputs.get("monthly_income", 0)
        interest_rate = user_inputs.get("interest_rate")
        down_payment = user_inputs.get("down_payment")

        # Get price score from previous step
        price_data = result_json.get("price", {})
        price_score = price_data.get("assessment", {}).get("score", 5.0)

        # Delegate to FinancingEvaluator
        assessment = self.financing_evaluator.evaluate(
            asking_price=deal.asking_price,
            financing_type=financing_type,
            price_score=price_score,
            interest_rate=interest_rate,
            down_payment=down_payment,
            monthly_income=monthly_income,
        )

        return {"assessment": assessment, "completed": True}

    async def _evaluate_risk(self, deal: Deal, result_json: dict) -> dict[str, Any]:
        """Evaluate risk factors using RiskEvaluator."""
        user_inputs = result_json.get("user_inputs", {})

        # Get data from previous steps
        condition_data = result_json.get("vehicle_condition", {})
        recommended_inspection = condition_data.get("assessment", {}).get(
            "recommended_inspection", True
        )
        inspection_completed = user_inputs.get("inspection_completed", False)

        price_data = result_json.get("price", {})
        fair_value = price_data.get("assessment", {}).get("fair_value")

        # Delegate to RiskEvaluator
        assessment = self.risk_evaluator.evaluate(
            vehicle_year=deal.vehicle_year,
            vehicle_mileage=deal.vehicle_mileage,
            asking_price=deal.asking_price,
            fair_value=fair_value,
            inspection_completed=inspection_completed,
            recommended_inspection=recommended_inspection,
        )

        return {"assessment": assessment, "completed": True}

    async def _evaluate_final(self, deal: Deal, result_json: dict) -> dict[str, Any]:
        """Generate final comprehensive evaluation."""
        # Compile all previous steps
        condition_data = result_json.get("vehicle_condition", {})
        price_data = result_json.get("price", {})
        financing_data = result_json.get("financing", {})
        risk_data = result_json.get("risk", {})

        # Calculate overall score using weighted formula
        condition_score = condition_data.get("assessment", {}).get("condition_score", 5.0)
        price_score = price_data.get("assessment", {}).get("score", 5.0)
        risk_score = risk_data.get("assessment", {}).get("risk_score", 5.0)

        overall_score = (
            (condition_score * EvaluationConfig.WEIGHT_CONDITION)
            + (price_score * EvaluationConfig.WEIGHT_PRICE)
            + ((11 - risk_score) * EvaluationConfig.WEIGHT_RISK)
        )
        overall_score = round(min(10.0, max(1.0, overall_score)), 1)

        # Generate recommendation
        if overall_score >= EvaluationConfig.FINAL_HIGHLY_RECOMMENDED:
            recommendation = "Highly Recommended - This is an excellent deal"
        elif overall_score >= EvaluationConfig.FINAL_RECOMMENDED:
            recommendation = "Recommended - Good deal with minor considerations"
        elif overall_score >= EvaluationConfig.FINAL_FAIR:
            recommendation = "Fair Deal - Proceed with caution"
        else:
            recommendation = "Not Recommended - Consider other options"

        # Compile next steps
        next_steps = []
        if condition_data.get("assessment", {}).get("recommended_inspection"):
            next_steps.append("Schedule a pre-purchase inspection")
        if risk_data.get("assessment", {}).get("risk_score", 0) > 6:
            next_steps.append("Review all risk factors carefully")

        price_insights = price_data.get("assessment", {}).get("talking_points", [])
        if price_insights:
            next_steps.append("Use provided talking points for negotiation")

        assessment = {
            "overall_score": overall_score,
            "recommendation": recommendation,
            "summary": {
                "condition_score": condition_score,
                "price_score": price_score,
                "risk_score": risk_score,
            },
            "next_steps": next_steps,
            "estimated_total_cost": financing_data.get("assessment", {}).get(
                "total_cost", deal.asking_price
            ),
        }

        return {"assessment": assessment, "completed": True}
