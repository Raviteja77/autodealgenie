"""
Pricing Evaluator Module

Integrates MarketCheck API and provides unified pricing strategy with LLM evaluation.
"""

import logging
from typing import Any

from app.core.evaluation_config import EvaluationConfig
from app.llm import generate_structured_json, llm_client
from app.llm.schemas import DealEvaluation
from app.services.marketcheck_service import marketcheck_service
from app.utils.error_handler import ApiError, MarketDataError

logger = logging.getLogger(__name__)


class PricingEvaluator:
    """Evaluates pricing using MarketCheck API and LLM-powered insights."""

    async def evaluate(
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
        Evaluate deal pricing with unified MarketCheck and LLM strategy.

        Args:
            vehicle_vin: Vehicle Identification Number
            asking_price: Asking price in USD
            condition: Vehicle condition description
            mileage: Current mileage in miles
            make: Vehicle make (optional)
            model: Vehicle model (optional)
            year: Vehicle year (optional)
            zip_code: ZIP code for location-based pricing (optional)

        Returns:
            Dictionary with fair_value, score, insights, talking_points, and optional market_data
        """
        logger.info(f"Evaluating pricing for VIN: {vehicle_vin}, Price: ${asking_price:,.2f}")

        # Try to get ML-based price prediction from MarketCheck
        market_price_data = await self._get_market_data(vehicle_vin, mileage, zip_code)

        # Use LLM for comprehensive evaluation
        if llm_client.is_available():
            try:
                return await self._llm_evaluation(
                    vehicle_vin,
                    asking_price,
                    condition,
                    mileage,
                    make,
                    model,
                    year,
                    market_price_data,
                )
            except Exception as e:
                logger.error(f"LLM evaluation failed: {e}. Falling back to market/heuristic.")
                # Fall through to market-based or heuristic evaluation

        # Fallback: Use MarketCheck data if available, otherwise heuristic
        if market_price_data:
            return self._marketcheck_evaluation(
                vehicle_vin, asking_price, condition, mileage, market_price_data
            )
        else:
            return self._heuristic_evaluation(vehicle_vin, asking_price, condition, mileage)

    async def _get_market_data(
        self, vehicle_vin: str, mileage: int, zip_code: str | None
    ) -> dict[str, Any] | None:
        """
        Fetch market data from MarketCheck API with error handling.

        Args:
            vehicle_vin: Vehicle VIN
            mileage: Current mileage
            zip_code: Optional ZIP code

        Returns:
            Market data dict or None if unavailable

        Raises:
            MarketDataError: If MarketCheck API fails critically
        """
        if not marketcheck_service.is_available():
            logger.debug("MarketCheck service not available")
            return None

        try:
            logger.info(f"Getting ML price prediction from MarketCheck for VIN: {vehicle_vin}")
            market_data = await marketcheck_service.get_price_prediction(
                vin=vehicle_vin, mileage=mileage, zip_code=zip_code, use_cache=True
            )
            logger.info(
                f"MarketCheck price prediction: ${market_data['predicted_price']:,.2f} "
                f"(confidence: {market_data['confidence']})"
            )
            return market_data
        except ApiError as e:
            logger.warning(
                f"MarketCheck API error: {e.message}. Continuing without market data."
            )
            # Don't raise - gracefully degrade
            return None
        except Exception as e:
            logger.warning(f"Unexpected MarketCheck error: {e}. Continuing without market data.")
            return None

    async def _llm_evaluation(
        self,
        vehicle_vin: str,
        asking_price: float,
        condition: str,
        mileage: int,
        make: str | None,
        model: str | None,
        year: int | None,
        market_data: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """
        LLM-powered evaluation with optional MarketCheck context.

        Args:
            vehicle_vin: Vehicle VIN
            asking_price: Asking price
            condition: Condition description
            mileage: Mileage
            make: Vehicle make
            model: Vehicle model
            year: Vehicle year
            market_data: Optional MarketCheck data

        Returns:
            Evaluation result dictionary
        """
        logger.debug(
            f"Calling LLM for evaluation - VIN: {vehicle_vin}, "
            f"Make: {make or 'Unknown'}, Model: {model or 'Unknown'}, "
            f"Year: {year or 'Unknown'}, Condition: {condition}"
        )

        # Prepare LLM prompt variables
        variables = {
            "vin": vehicle_vin,
            "make": make or "Unknown",
            "model": model or "Unknown",
            "year": str(year) if year else "Unknown",
            "asking_price": asking_price,
            "mileage": mileage,
            "condition": condition,
        }

        # Add MarketCheck context if available
        if market_data:
            variables["market_predicted_price"] = market_data["predicted_price"]
            variables["market_confidence"] = market_data["confidence"]
            variables["market_price_range"] = (
                f"${market_data['price_range']['min']:,.0f} - "
                f"${market_data['price_range']['max']:,.0f}"
            )
            prompt_id = "evaluation_with_market"
        else:
            prompt_id = "evaluation"

        # Use centralized LLM client with evaluator role
        evaluation = generate_structured_json(
            prompt_id=prompt_id,
            variables=variables,
            response_model=DealEvaluation,
            temperature=0.7,
            agent_role="evaluator",
        )

        logger.info(f"LLM evaluation successful - Score: {evaluation.score}/10")

        # Convert to dict and apply limits
        result = {
            "fair_value": evaluation.fair_value,
            "score": evaluation.score,
            "insights": evaluation.insights[: EvaluationConfig.MAX_INSIGHTS],
            "talking_points": evaluation.talking_points[: EvaluationConfig.MAX_INSIGHTS],
        }

        # Include MarketCheck data if available
        if market_data:
            result["market_data"] = {
                "predicted_price": market_data["predicted_price"],
                "confidence": market_data["confidence"],
                "price_range": market_data["price_range"],
            }

        return result

    def _marketcheck_evaluation(
        self,
        vehicle_vin: str,
        asking_price: float,
        condition: str,
        mileage: int,
        market_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluation based on MarketCheck ML price prediction.

        Args:
            vehicle_vin: Vehicle VIN
            asking_price: Asking price
            condition: Condition
            mileage: Mileage
            market_data: MarketCheck prediction data

        Returns:
            Evaluation result dictionary
        """
        logger.info(
            f"Using MarketCheck-based evaluation for VIN: {vehicle_vin}, "
            f"Price: ${asking_price:,.2f}"
        )

        predicted_price = market_data["predicted_price"]
        confidence = market_data["confidence"]
        price_range = market_data["price_range"]

        # Calculate price difference
        price_diff = asking_price - predicted_price
        price_diff_pct = (price_diff / predicted_price) * 100 if predicted_price > 0 else 0

        # Calculate score based on price comparison
        score = self._calculate_price_score(price_diff_pct)

        # Adjust for condition
        from app.services.evaluation.condition import ConditionEvaluator

        condition_eval = ConditionEvaluator()
        score += condition_eval.get_condition_adjustment(condition)

        # Adjust for MarketCheck confidence
        if confidence == "low":
            score += EvaluationConfig.MARKETCHECK_LOW_CONFIDENCE_PENALTY

        # Clamp score
        score = max(1.0, min(10.0, score))

        # Generate insights and talking points
        insights = self._generate_market_insights(
            predicted_price, confidence, price_range, price_diff, price_diff_pct, mileage, condition
        )
        talking_points = self._generate_market_talking_points(
            predicted_price, price_diff, mileage
        )

        logger.info(
            f"MarketCheck evaluation completed - VIN: {vehicle_vin}, "
            f"Score: {score:.1f}/10, Market Price: ${predicted_price:,.2f}"
        )

        return {
            "fair_value": round(predicted_price, 2),
            "score": round(score, 1),
            "insights": insights[: EvaluationConfig.MAX_INSIGHTS],
            "talking_points": talking_points[: EvaluationConfig.MAX_INSIGHTS],
            "market_data": {
                "predicted_price": predicted_price,
                "confidence": confidence,
                "price_range": price_range,
            },
        }

    def _heuristic_evaluation(
        self, vehicle_vin: str, asking_price: float, condition: str, mileage: int
    ) -> dict[str, Any]:
        """
        Heuristic-based evaluation when both LLM and MarketCheck are unavailable.

        Args:
            vehicle_vin: Vehicle VIN
            asking_price: Asking price
            condition: Condition
            mileage: Mileage

        Returns:
            Basic evaluation dictionary
        """
        logger.warning(
            f"Using heuristic evaluation for VIN: {vehicle_vin}, "
            f"Price: ${asking_price:,.2f}, Condition: {condition}, Mileage: {mileage:,}"
        )

        from app.services.evaluation.condition import ConditionEvaluator

        condition_eval = ConditionEvaluator()

        # Base score
        score = 5.0

        # Adjust for condition
        score += condition_eval.get_condition_adjustment(condition)

        # Adjust for mileage
        mileage_assessment, mileage_adjustment = condition_eval.get_mileage_assessment(mileage)
        score += mileage_adjustment

        # Clamp score
        score = max(1.0, min(10.0, score))

        # Estimate fair value
        fair_value_adjustment = (score - 5.0) / 10.0
        fair_value = asking_price * (1.0 - fair_value_adjustment * 0.1)

        # Generate insights
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

        # Generate talking points
        talking_points = [
            "Request a detailed vehicle history report (Carfax/AutoCheck)",
            "Ask for maintenance records to verify condition claims",
        ]

        if mileage > EvaluationConfig.RISK_MODERATE_MILEAGE_THRESHOLD:
            talking_points.append(
                f"Use the {mileage:,}-mile reading as leverage for price negotiation"
            )

        if price_diff > 1000:
            talking_points.append(
                f"Mention that comparable vehicles are priced around ${fair_value:,.0f}"
            )

        talking_points.append("Request a pre-purchase inspection by an independent mechanic")

        logger.info(
            f"Heuristic evaluation completed - VIN: {vehicle_vin}, "
            f"Score: {score:.1f}/10, Fair Value: ${fair_value:,.2f}"
        )

        return {
            "fair_value": round(fair_value, 2),
            "score": round(score, 1),
            "insights": insights,
            "talking_points": talking_points,
        }

    def _calculate_price_score(self, price_diff_pct: float) -> float:
        """
        Calculate score based on price difference percentage.

        Args:
            price_diff_pct: Price difference as percentage

        Returns:
            Score value (1-10)
        """
        if price_diff_pct <= EvaluationConfig.PRICE_EXCELLENT_DISCOUNT:
            return EvaluationConfig.PRICE_SCORE_EXCELLENT
        elif price_diff_pct <= EvaluationConfig.PRICE_GREAT_DISCOUNT:
            return EvaluationConfig.PRICE_SCORE_GREAT
        elif price_diff_pct <= EvaluationConfig.PRICE_GOOD_DISCOUNT:
            return EvaluationConfig.PRICE_SCORE_GOOD
        elif price_diff_pct <= EvaluationConfig.PRICE_AT_MARKET:
            return EvaluationConfig.PRICE_SCORE_AT_MARKET
        elif price_diff_pct <= EvaluationConfig.PRICE_SLIGHT_PREMIUM:
            return EvaluationConfig.PRICE_SCORE_SLIGHT_PREMIUM
        elif price_diff_pct <= EvaluationConfig.PRICE_MODERATE_PREMIUM:
            return EvaluationConfig.PRICE_SCORE_MODERATE_PREMIUM
        elif price_diff_pct <= EvaluationConfig.PRICE_HIGH_PREMIUM:
            return EvaluationConfig.PRICE_SCORE_HIGH_PREMIUM
        else:
            return EvaluationConfig.PRICE_SCORE_VERY_HIGH_PREMIUM

    def _generate_market_insights(
        self,
        predicted_price: float,
        confidence: str,
        price_range: dict,
        price_diff: float,
        price_diff_pct: float,
        mileage: int,
        condition: str,
    ) -> list[str]:
        """Generate insights based on market data."""
        insights = []
        insights.append(
            f"MarketCheck ML model predicts fair value at ${predicted_price:,.2f} "
            f"(confidence: {confidence})"
        )
        insights.append(
            f"Market price range: ${price_range['min']:,.2f} - ${price_range['max']:,.2f}"
        )

        if abs(price_diff) > 500:
            if price_diff > 0:
                insights.append(
                    f"Asking price is ${price_diff:,.0f} ({price_diff_pct:+.1f}%) "
                    f"above market prediction"
                )
            else:
                insights.append(
                    f"Asking price is ${abs(price_diff):,.0f} ({abs(price_diff_pct):.1f}%) "
                    f"below market prediction - excellent value!"
                )

        # Mileage assessment
        if mileage < EvaluationConfig.MILEAGE_EXCEPTIONALLY_LOW:
            insights.append(f"Exceptionally low mileage at {mileage:,} miles")
        elif mileage < EvaluationConfig.MILEAGE_LOW:
            insights.append(f"Low mileage at {mileage:,} miles")
        elif mileage > EvaluationConfig.MILEAGE_MODERATE:
            insights.append(f"High mileage at {mileage:,} miles - factor into negotiations")

        insights.append(f"Condition reported as '{condition}'")

        return insights

    def _generate_market_talking_points(
        self, predicted_price: float, price_diff: float, mileage: int
    ) -> list[str]:
        """Generate talking points based on market data."""
        talking_points = []

        if price_diff > 1000:
            talking_points.append(
                f"Reference MarketCheck data showing fair value around ${predicted_price:,.0f}"
            )
            talking_points.append(
                f"Ask for justification of ${price_diff:,.0f} premium over market prediction"
            )
        elif price_diff < -1000:
            talking_points.append(
                "This is priced below market - verify condition and history carefully"
            )

        talking_points.append("Request complete vehicle history report (Carfax/AutoCheck)")
        talking_points.append("Verify all maintenance records match condition claims")

        if mileage > EvaluationConfig.RISK_MODERATE_MILEAGE_THRESHOLD:
            talking_points.append(f"Use {mileage:,}-mile reading as negotiation leverage")

        talking_points.append("Schedule pre-purchase inspection by certified mechanic")

        return talking_points
