"""
Risk Evaluator Module

Factors and simplifies age, mileage, and price-delta risk scoring.
"""

import logging
from datetime import datetime
from typing import Any

from app.core.evaluation_config import EvaluationConfig

logger = logging.getLogger(__name__)


class RiskEvaluator:
    """Evaluates risk factors for vehicle deals."""

    def evaluate(
        self,
        vehicle_year: int,
        vehicle_mileage: int,
        asking_price: float,
        fair_value: float | None = None,
        inspection_completed: bool = False,
        recommended_inspection: bool = True,
    ) -> dict[str, Any]:
        """
        Evaluate risk factors.

        Args:
            vehicle_year: Vehicle year
            vehicle_mileage: Current mileage
            asking_price: Asking price
            fair_value: Fair value from pricing evaluation (optional)
            inspection_completed: Whether inspection has been completed
            recommended_inspection: Whether inspection is recommended

        Returns:
            Dictionary with risk_score, risk_factors, and recommendation
        """
        logger.info(
            f"Evaluating risk for {vehicle_year} vehicle with {vehicle_mileage:,} miles, "
            f"Price: ${asking_price:,.2f}"
        )

        risk_factors = []
        risk_score = EvaluationConfig.RISK_BASE_SCORE

        # High mileage risk
        if vehicle_mileage > EvaluationConfig.RISK_HIGH_MILEAGE_THRESHOLD:
            risk_factors.append("High mileage increases maintenance risk")
            risk_score += EvaluationConfig.RISK_HIGH_MILEAGE_PENALTY
        elif vehicle_mileage > EvaluationConfig.RISK_MODERATE_MILEAGE_THRESHOLD:
            risk_factors.append("Moderate mileage - monitor maintenance history")
            risk_score += EvaluationConfig.RISK_MODERATE_MILEAGE_PENALTY

        # Age risk
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle_year
        if vehicle_age > EvaluationConfig.RISK_OLD_AGE_THRESHOLD:
            risk_factors.append("Vehicle is over 10 years old - check for wear and tear")
            risk_score += EvaluationConfig.RISK_OLD_AGE_PENALTY
        elif vehicle_age > EvaluationConfig.RISK_MODERATE_AGE_THRESHOLD:
            risk_factors.append("Vehicle age warrants thorough inspection")
            risk_score += EvaluationConfig.RISK_MODERATE_AGE_PENALTY

        # Inspection risk
        if recommended_inspection and not inspection_completed:
            risk_factors.append("Pre-purchase inspection strongly recommended")
            risk_score += EvaluationConfig.RISK_INSPECTION_RECOMMENDED_PENALTY

        # Price risk
        if fair_value:
            price_diff = asking_price - fair_value
            if price_diff > EvaluationConfig.RISK_PRICE_PREMIUM_THRESHOLD:
                risk_factors.append(f"Vehicle priced ${price_diff:,.0f} above fair value")
                risk_score += EvaluationConfig.RISK_PRICE_PREMIUM_PENALTY

        # Clamp risk score
        risk_score = min(10.0, max(1.0, risk_score))

        # Generate recommendation
        recommendation = self._generate_recommendation(risk_score)

        logger.info(
            f"Risk evaluation completed - Score: {risk_score:.1f}/10, "
            f"Factors: {len(risk_factors)}"
        )

        return {
            "risk_score": round(risk_score, 1),
            "risk_factors": risk_factors,
            "recommendation": recommendation,
        }

    def _generate_recommendation(self, risk_score: float) -> str:
        """
        Generate recommendation based on risk score.

        Args:
            risk_score: Calculated risk score (1-10, lower is better)

        Returns:
            Risk recommendation string
        """
        if risk_score < EvaluationConfig.RISK_LOW_THRESHOLD:
            return "Low risk - proceed with confidence"
        elif risk_score < EvaluationConfig.RISK_MODERATE_THRESHOLD:
            return "Moderate risk - proceed with caution"
        else:
            return "High risk - consider alternatives"
