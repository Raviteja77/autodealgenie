"""
Deal Evaluation Service
Provides fair market value analysis and negotiation insights for vehicle deals
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.redis import redis_client
from app.llm import generate_structured_json, llm_client
from app.llm.schemas import DealEvaluation, VehicleConditionAssessment
from app.models.evaluation import EvaluationStatus, PipelineStep
from app.models.models import Deal
from app.repositories.ai_response_repository import ai_response_repository
from app.repositories.evaluation_repository import EvaluationRepository
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)


class DealEvaluationService:
    """Service for evaluating car deals and providing negotiation insights"""

    MAX_INSIGHTS = 5  # Maximum number of insights/talking points to return

    # Affordability thresholds (payment-to-income ratio percentages)
    AFFORDABILITY_EXCELLENT = 10  # ≤ 10% is excellent
    AFFORDABILITY_GOOD = 15  # ≤ 15% is good
    AFFORDABILITY_MODERATE = 20  # ≤ 20% is moderate

    # Deal quality thresholds for financing recommendations
    EXCELLENT_DEAL_SCORE = 8.0  # >= 8.0 is excellent deal
    GOOD_DEAL_SCORE = 6.5  # >= 6.5 is good deal
    LENDER_RECOMMENDATION_MIN_SCORE = 6.5  # Minimum score for lender recommendations

    # Interest rate thresholds for financing recommendations
    LOW_INTEREST_RATE = 4.0  # ≤ 4% is considered low/excellent
    REASONABLE_INTEREST_RATE = 5.0  # ≤ 5% is considered reasonable/good
    HIGH_INTEREST_THRESHOLD = 20  # Interest cost > 20% of purchase price is high

    # Default loan parameters
    DEFAULT_DOWN_PAYMENT_RATIO = 0.2  # 20% down payment
    DEFAULT_LOAN_TERM_MONTHS = 60  # 5-year term

    # Cache settings
    CACHE_TTL = 3600  # Cache evaluation results for 1 hour (in seconds)
    CACHE_KEY_PREFIX = "deal_eval"  # Prefix for cache keys

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
        Generate a unique cache key based on all evaluation-affecting parameters

        Args:
            vehicle_vin: Vehicle Identification Number
            asking_price: Asking price in USD
            condition: Vehicle condition descriptor (e.g., "excellent", "good")
            mileage: Vehicle mileage in miles
            make: Vehicle make (optional)
            model: Vehicle model (optional)
            year: Vehicle year (optional)

        Returns:
            Cache key string
        """
        # Create a deterministic hash from all evaluation-affecting parameters
        key_payload: dict[str, Any] = {
            "vin": vehicle_vin,
            "asking_price": round(asking_price, 2),
            "condition": condition.lower(),  # Normalize condition
            "mileage": mileage,
        }
        if make is not None:
            key_payload["make"] = make.lower()
        if model is not None:
            key_payload["model"] = model.lower()
        if year is not None:
            key_payload["year"] = year

        # Use JSON for deterministic key generation
        key_data = json.dumps(key_payload, sort_keys=True, separators=(",", ":"))
        # Use SHA-256 for better security practices
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        return f"{self.CACHE_KEY_PREFIX}:{key_hash}"

    async def _get_cached_evaluation(self, cache_key: str) -> dict[str, Any] | None:
        """
        Retrieve cached evaluation result from Redis

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
        Store evaluation result in Redis cache

        Args:
            cache_key: Cache key to store under
            evaluation: Evaluation result to cache
        """
        try:
            redis = redis_client.get_client()
            if redis is None:
                logger.debug("Redis client not available, skipping cache set")
                return

            await redis.setex(cache_key, self.CACHE_TTL, json.dumps(evaluation))
            logger.info(f"Cached evaluation for key: {cache_key} (TTL: {self.CACHE_TTL}s)")
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
    ) -> dict[str, Any]:
        """
        Evaluate a car deal and provide comprehensive analysis

        This method implements Redis caching to avoid redundant LLM calls for
        deals that have already been evaluated with the same VIN and price.

        Args:
            vehicle_vin: 17-character Vehicle Identification Number
            asking_price: Asking price in USD
            condition: Vehicle condition description
            mileage: Current mileage in miles
            make: Vehicle make (optional, improves evaluation accuracy)
            model: Vehicle model (optional, improves evaluation accuracy)
            year: Vehicle year (optional, improves evaluation accuracy)

        Returns:
            Dictionary containing fair_value, score, insights, and talking_points
        """
        logger.info(f"Evaluating deal for VIN: {vehicle_vin}, Price: ${asking_price:,.2f}")

        # Generate cache key and check cache (includes all evaluation-affecting parameters)
        cache_key = self._generate_cache_key(
            vehicle_vin, asking_price, condition, mileage, make, model, year
        )
        cached_result = await self._get_cached_evaluation(cache_key)

        if cached_result:
            logger.info(f"Returning cached evaluation for VIN: {vehicle_vin}")
            return cached_result

        # Check if LLM client is available
        if not llm_client.is_available():
            logger.warning("LLM client not available, using fallback evaluation")
            return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)

        try:
            logger.debug(
                f"Calling LLM for evaluation - VIN: {vehicle_vin}, "
                f"Make: {make or 'Unknown'}, Model: {model or 'Unknown'}, "
                f"Year: {year or 'Unknown'}, Condition: {condition}"
            )

            # Use centralized LLM client with the evaluation prompt
            evaluation = await generate_structured_json(
                prompt_id="evaluation",
                variables={
                    "vin": vehicle_vin,
                    "make": make or "Unknown",
                    "model": model or "Unknown",
                    "year": str(year) if year else "Unknown",
                    "asking_price": f"{asking_price:,.2f}",
                    "mileage": f"{mileage:,}",
                    "condition": condition,
                },
                response_model=DealEvaluation,
                temperature=0.7,
            )

            logger.info(f"LLM evaluation successful - Score: {evaluation.score}/10")

            # Convert Pydantic model to dict and ensure limits
            result = {
                "fair_value": evaluation.fair_value,
                "score": evaluation.score,
                "insights": evaluation.insights[: self.MAX_INSIGHTS],
                "talking_points": evaluation.talking_points[: self.MAX_INSIGHTS],
            }

            # Cache the successful result
            await self._set_cached_evaluation(cache_key, result)

            # Log AI response to MongoDB for analytics and traceability
            try:
                await ai_response_repository.create_response(
                    feature="deal_evaluation",
                    user_id=None,  # Deal evaluation is often anonymous
                    deal_id=None,  # May not be associated with a deal yet
                    prompt_id="evaluation",
                    prompt_variables={
                        "vin": vehicle_vin,
                        "make": make or "Unknown",
                        "model": model or "Unknown",
                        "year": year,
                        "asking_price": asking_price,
                        "mileage": mileage,
                        "condition": condition,
                    },
                    response_content=result,
                    response_metadata={
                        "score": evaluation.score,
                        "fair_value": evaluation.fair_value,
                    },
                    llm_used=True,
                )
            except Exception as log_error:
                logger.error(f"Failed to log evaluation AI response to MongoDB: {str(log_error)}")
                # Don't fail the main operation if logging fails

            return result

        # Note: The JSONDecodeError and ValueError handlers below are primarily for
        # catching errors from the caching logic (json.loads in _get_cached_evaluation).
        # The generate_structured_json function wraps LLM JSON/validation errors in ApiError,
        # which are caught by the ApiError handler below.
        except ApiError as e:
            logger.error(
                f"ApiError during deal evaluation: {e.message}. "
                f"Status: {e.status_code}, VIN: {vehicle_vin}, Price: ${asking_price:,.2f}"
            )
            logger.error(f"ApiError details: {e.details}")
            # For LLM-related ApiErrors, use fallback evaluation
            return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)
        except json.JSONDecodeError as e:
            logger.error(
                f"JSON parsing error during deal evaluation: {e}. "
                f"VIN: {vehicle_vin}, Price: ${asking_price:,.2f}. "
                "This may indicate a cache corruption issue."
            )
            logger.debug(f"JSON decode error details: line {e.lineno}, column {e.colno}")
            return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)
        except ValueError as e:
            logger.error(
                f"Validation error during deal evaluation: {e}. "
                f"VIN: {vehicle_vin}, Price: ${asking_price:,.2f}. "
                "This may indicate a data validation issue."
            )
            return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)
        except Exception as e:
            logger.error(
                f"Unexpected error during deal evaluation: {type(e).__name__}: {e}. "
                f"VIN: {vehicle_vin}, Price: ${asking_price:,.2f}"
            )
            logger.exception("Full traceback for debugging:")
            return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)

    def _fallback_evaluation(
        self, vehicle_vin: str, asking_price: float, condition: str, mileage: int
    ) -> dict[str, Any]:
        """
        Fallback evaluation logic when LLM is not available or fails

        Uses simple heuristics to provide basic evaluation
        """
        logger.warning(
            f"Using fallback evaluation for VIN: {vehicle_vin}, "
            f"Price: ${asking_price:,.2f}, Condition: {condition}, Mileage: {mileage:,}"
        )

        # Simple scoring based on condition and mileage
        score = 5.0  # Base score

        # Adjust for condition
        condition_lower = condition.lower()
        if "excellent" in condition_lower or "like new" in condition_lower:
            score += 1.5
        elif "good" in condition_lower or "very good" in condition_lower:
            score += 0.5
        elif "fair" in condition_lower:
            score -= 0.5
        elif "poor" in condition_lower:
            score -= 1.5

        # Adjust for mileage
        if mileage < 30000:
            score += 1.0
            mileage_assessment = "exceptionally low mileage"
        elif mileage < 60000:
            score += 0.5
            mileage_assessment = "low mileage"
        elif mileage < 100000:
            mileage_assessment = "moderate mileage"
        elif mileage < 150000:
            score -= 0.5
            mileage_assessment = "high mileage"
        else:
            score -= 1.0
            mileage_assessment = "very high mileage"

        # Clamp score between 1 and 10
        score = max(1.0, min(10.0, score))

        # Estimate fair value (simplified: 5% discount for good deals, adjust based on score)
        fair_value_adjustment = (score - 5.0) / 10.0  # Range: -0.4 to +0.5
        fair_value = asking_price * (1.0 - fair_value_adjustment * 0.1)

        # Generate basic insights
        insights = [
            f"Vehicle has {mileage_assessment} at {mileage:,} miles",
            f"Condition reported as '{condition}'",
            f"Deal score: {score:.1f}/10 based on available information",
        ]

        price_diff = asking_price - fair_value
        if abs(price_diff) > 500:
            if price_diff > 0:
                insights.append(
                    f"Asking price is approximately ${price_diff:,.0f} above estimated fair value"
                )
            else:
                insights.append(
                    f"Asking price is approximately ${abs(price_diff):,.0f} below estimated fair value"
                )

        # Generate basic talking points
        talking_points = [
            "Request a detailed vehicle history report (Carfax/AutoCheck)",
            "Ask for maintenance records to verify condition claims",
        ]

        if mileage > 75000:
            talking_points.append(
                f"Use the {mileage:,}-mile reading as leverage for price negotiation"
            )

        if price_diff > 1000:
            talking_points.append(
                f"Mention that comparable vehicles are priced around ${fair_value:,.0f}"
            )

        talking_points.append("Request a pre-purchase inspection by an independent mechanic")

        logger.info(
            f"Fallback evaluation completed - VIN: {vehicle_vin}, "
            f"Score: {score:.1f}/10, Fair Value: ${fair_value:,.2f}"
        )

        return {
            "fair_value": round(fair_value, 2),
            "score": round(score, 1),
            "insights": insights,
            "talking_points": talking_points,
        }

    # Multi-step pipeline methods

    async def process_evaluation_step(
        self, db: Session, evaluation_id: int, user_answers: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Process the current step of an evaluation pipeline

        Args:
            db: Database session
            evaluation_id: Evaluation ID
            user_answers: Optional answers to previous questions

        Returns:
            Dictionary containing step result with either assessment or questions
        """
        repo = EvaluationRepository(db)
        evaluation = repo.get(evaluation_id)

        if not evaluation:
            raise ValueError(f"Evaluation {evaluation_id} not found")

        # Get the deal details
        deal = db.query(Deal).filter(Deal.id == evaluation.deal_id).first()
        if not deal:
            raise ValueError(f"Deal {evaluation.deal_id} not found")

        current_step = evaluation.current_step
        result_json = evaluation.result_json or {}

        # If user provided answers, incorporate them
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

        # Update evaluation based on step result
        if step_result.get("questions"):
            # If questions are returned, update status to awaiting_input
            result_json[current_step.value] = step_result
            repo.update_result(evaluation_id, result_json, EvaluationStatus.AWAITING_INPUT)
        else:
            # If no questions, advance to next step
            result_json[current_step.value] = step_result
            next_step = self._get_next_step(current_step)

            if next_step:
                repo.update_step(evaluation_id, next_step)
                repo.update_result(evaluation_id, result_json, EvaluationStatus.ANALYZING)
            else:
                # Final step completed
                repo.update_result(evaluation_id, result_json, EvaluationStatus.COMPLETED)

        return step_result

    def _get_next_step(self, current_step: PipelineStep) -> PipelineStep | None:
        """Get the next step in the pipeline"""
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
        """Evaluate vehicle condition step"""
        user_inputs = result_json.get("user_inputs", {})

        # Check if we have required data
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

        # Use LLM to evaluate condition
        if llm_client.is_available():
            try:
                assessment_result = generate_structured_json(
                    prompt_id="vehicle_condition",
                    variables={
                        "make": deal.vehicle_make or "Unknown",
                        "model": deal.vehicle_model or "Unknown",
                        "year": str(deal.vehicle_year) if deal.vehicle_year else "Unknown",
                        "vin": user_inputs.get("vin", "Unknown"),
                        "mileage": f"{deal.vehicle_mileage:,}",
                        "condition_description": user_inputs.get(
                            "condition_description", "Not provided"
                        ),
                    },
                    response_model=VehicleConditionAssessment,
                    temperature=0.7,
                    agent_role="evaluator",
                )

                assessment = {
                    "condition_score": assessment_result.condition_score,
                    "condition_notes": assessment_result.condition_notes,
                    "recommended_inspection": assessment_result.recommended_inspection,
                }
                logger.info(
                    f"Vehicle condition assessment completed successfully. "
                    f"Score: {assessment_result.condition_score}/10"
                )
            except Exception as e:
                logger.error(
                    f"LLM evaluation error for vehicle condition: {type(e).__name__}: {e}. "
                    f"VIN: {user_inputs.get('vin', 'Unknown')}, "
                    f"Deal ID: {deal.id}. Using fallback assessment."
                )
                logger.exception("Full traceback for vehicle condition evaluation error:")
                assessment = {
                    "condition_score": 7.0,
                    "condition_notes": ["Unable to perform detailed analysis due to LLM error"],
                    "recommended_inspection": True,
                }
        else:
            # Fallback assessment
            logger.warning("LLM client not available for vehicle condition assessment")
            assessment = {
                "condition_score": 7.0,
                "condition_notes": ["Condition evaluation requires LLM service"],
                "recommended_inspection": True,
            }

        return {"assessment": assessment, "completed": True}

    async def _evaluate_price(self, deal: Deal, result_json: dict) -> dict[str, Any]:
        """Evaluate price step"""
        # Use existing evaluate_deal logic
        user_inputs = result_json.get("user_inputs", {})
        vin = user_inputs.get("vin", "UNKNOWN")
        condition = user_inputs.get("condition_description", "unknown")

        price_eval = await self.evaluate_deal(
            vehicle_vin=vin,
            asking_price=deal.asking_price,
            condition=condition,
            mileage=deal.vehicle_mileage,
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
        """Evaluate financing step with comprehensive affordability analysis"""
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

        # Get price evaluation data for comparison
        price_data = result_json.get("price", {})
        price_score = price_data.get("assessment", {}).get("score", 5.0)

        if financing_type == "cash":
            # Cash purchase assessment
            affordability_notes = ["No monthly payments required", "No interest costs"]
            affordability_score = 10.0  # Best affordability for cash

            # Determine if cash is better based on deal quality
            if price_score >= 7.0:
                recommendation = "cash"
                recommendation_reason = (
                    "This is a good deal - paying cash avoids interest and saves money long-term"
                )
            else:
                recommendation = "either"
                recommendation_reason = "Cash eliminates interest costs, but consider financing if you want to preserve liquidity"

            assessment = {
                "financing_type": "cash",
                "monthly_payment": None,
                "total_cost": deal.asking_price,
                "total_interest": None,
                "affordability_score": affordability_score,
                "affordability_notes": affordability_notes,
                "recommendation": recommendation,
                "recommendation_reason": recommendation_reason,
                "cash_vs_financing_savings": None,
            }
        else:
            # Financing assessment
            interest_rate = user_inputs.get("interest_rate", 5.5)
            down_payment = user_inputs.get(
                "down_payment", deal.asking_price * self.DEFAULT_DOWN_PAYMENT_RATIO
            )
            loan_amount = deal.asking_price - down_payment

            # Calculate monthly payment
            monthly_rate = interest_rate / 100 / 12
            months = self.DEFAULT_LOAN_TERM_MONTHS
            if monthly_rate > 0:
                monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** months) / (
                    (1 + monthly_rate) ** months - 1
                )
            else:
                monthly_payment = loan_amount / months

            total_cost = down_payment + (monthly_payment * months)
            total_interest = total_cost - deal.asking_price

            # Calculate affordability metrics
            affordability_notes = []
            affordability_score = 5.0  # Base score

            # Check monthly payment affordability (industry guideline)
            # Division by monthly_income is safe here due to the > 0 check
            if monthly_income > 0:
                payment_ratio = (monthly_payment / monthly_income) * 100
                if payment_ratio <= self.AFFORDABILITY_EXCELLENT:
                    affordability_notes.append(
                        f"Excellent: Payment is {payment_ratio:.1f}% of monthly income"
                    )
                    affordability_score = 9.0
                elif payment_ratio <= self.AFFORDABILITY_GOOD:
                    affordability_notes.append(
                        f"Good: Payment is {payment_ratio:.1f}% of monthly income"
                    )
                    affordability_score = 7.0
                elif payment_ratio <= self.AFFORDABILITY_MODERATE:
                    affordability_notes.append(
                        f"Moderate: Payment is {payment_ratio:.1f}% of monthly income"
                    )
                    affordability_score = 5.0
                else:
                    affordability_notes.append(
                        f"Warning: Payment is {payment_ratio:.1f}% of monthly income (high)"
                    )
                    affordability_score = 3.0
            else:
                affordability_notes.append("Unable to assess affordability without income data")

            # Add interest cost note
            if total_interest > 0:
                interest_percent = (total_interest / deal.asking_price) * 100
                if interest_percent > self.HIGH_INTEREST_THRESHOLD:
                    affordability_notes.append(
                        f"High interest cost: ${total_interest:,.0f} ({interest_percent:.1f}% of purchase price)"
                    )
                else:
                    affordability_notes.append(
                        f"Interest cost: ${total_interest:,.0f} over {months} months"
                    )

            # Compare cash vs financing
            cash_savings = total_interest  # How much you save by paying cash

            # Generate financing recommendation
            if price_score >= self.EXCELLENT_DEAL_SCORE:
                # Excellent deal
                if interest_rate <= self.LOW_INTEREST_RATE:
                    recommendation = "financing"
                    recommendation_reason = "Excellent deal with low interest rate - financing preserves cash for other investments"
                else:
                    recommendation = "either"
                    recommendation_reason = (
                        "Excellent deal, but moderate interest rate - consider your cash position"
                    )
            elif price_score >= self.GOOD_DEAL_SCORE:
                # Good deal
                if interest_rate <= self.REASONABLE_INTEREST_RATE:
                    recommendation = "financing"
                    recommendation_reason = (
                        "Good deal with reasonable rate - financing is a viable option"
                    )
                else:
                    recommendation = "cash"
                    recommendation_reason = f"Good deal but interest costs add ${total_interest:,.0f} - cash is better if available"
            else:
                # Fair or poor deal
                recommendation = "cash"
                recommendation_reason = (
                    "Deal quality is mediocre - avoid paying interest on an overpriced vehicle"
                )
                if affordability_score < 5.0:
                    recommendation_reason += ". Payment may also strain your budget."

            assessment = {
                "financing_type": financing_type,
                "loan_amount": round(loan_amount, 2),
                "monthly_payment": round(monthly_payment, 2),
                "total_cost": round(total_cost, 2),
                "total_interest": round(total_interest, 2),
                "affordability_score": round(affordability_score, 1),
                "affordability_notes": affordability_notes,
                "recommendation": recommendation,
                "recommendation_reason": recommendation_reason,
                "cash_vs_financing_savings": round(cash_savings, 2),
            }

        return {"assessment": assessment, "completed": True}

    async def _evaluate_risk(self, deal: Deal, result_json: dict) -> dict[str, Any]:
        """Evaluate risk factors"""
        user_inputs = result_json.get("user_inputs", {})

        risk_factors = []
        risk_score = 5.0  # Base risk score (1-10, lower is better)

        # High mileage risk
        if deal.vehicle_mileage > 100000:
            risk_factors.append("High mileage increases maintenance risk")
            risk_score += 1.5
        elif deal.vehicle_mileage > 75000:
            risk_factors.append("Moderate mileage - monitor maintenance history")
            risk_score += 0.5

        # Age risk
        current_year = datetime.now().year
        vehicle_age = current_year - deal.vehicle_year
        if vehicle_age > 10:
            risk_factors.append("Vehicle is over 10 years old - check for wear and tear")
            risk_score += 1.0
        elif vehicle_age > 7:
            risk_factors.append("Vehicle age warrants thorough inspection")
            risk_score += 0.5

        # Missing inspection risk
        condition_data = result_json.get("vehicle_condition", {})
        if condition_data.get("assessment", {}).get("recommended_inspection"):
            if not user_inputs.get("inspection_completed"):
                risk_factors.append("Pre-purchase inspection strongly recommended")
                risk_score += 1.5

        # Price risk
        price_data = result_json.get("price", {})
        if price_data:
            fair_value = price_data.get("assessment", {}).get("fair_value", deal.asking_price)
            price_diff = deal.asking_price - fair_value
            if price_diff > 2000:
                risk_factors.append(f"Vehicle priced ${price_diff:,.0f} above fair value")
                risk_score += 1.0

        risk_score = min(10.0, max(1.0, risk_score))

        assessment = {
            "risk_score": round(risk_score, 1),
            "risk_factors": risk_factors,
            "recommendation": (
                "Low risk - proceed with confidence"
                if risk_score < 4
                else (
                    "Moderate risk - proceed with caution"
                    if risk_score < 7
                    else "High risk - consider alternatives"
                )
            ),
        }

        return {"assessment": assessment, "completed": True}

    async def _evaluate_final(self, deal: Deal, result_json: dict) -> dict[str, Any]:
        """Generate final comprehensive evaluation"""
        # Compile all previous steps
        condition_data = result_json.get("vehicle_condition", {})
        price_data = result_json.get("price", {})
        financing_data = result_json.get("financing", {})
        risk_data = result_json.get("risk", {})

        # Calculate overall score
        condition_score = condition_data.get("assessment", {}).get("condition_score", 5.0)
        price_score = price_data.get("assessment", {}).get("score", 5.0)
        risk_score = risk_data.get("assessment", {}).get("risk_score", 5.0)

        # Overall score: weighted average (condition 20%, price 50%, risk 30% inverted)
        overall_score = (condition_score * 0.2) + (price_score * 0.5) + ((11 - risk_score) * 0.3)
        overall_score = round(min(10.0, max(1.0, overall_score)), 1)

        # Generate recommendation
        if overall_score >= 8.0:
            recommendation = "Highly Recommended - This is an excellent deal"
        elif overall_score >= 6.5:
            recommendation = "Recommended - Good deal with minor considerations"
        elif overall_score >= 5.0:
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
                "estimated_total_cost", deal.asking_price
            ),
        }

        return {"assessment": assessment, "completed": True}


# Singleton instance
deal_evaluation_service = DealEvaluationService()
