"""
Condition Evaluator Module

Assesses vehicle condition using LLM-based evaluation with the evaluator agent role.
"""

import logging
from typing import Any

from app.core.evaluation_config import EvaluationConfig
from app.llm import generate_structured_json, llm_client
from app.llm.schemas import VehicleConditionAssessment

logger = logging.getLogger(__name__)


class ConditionEvaluator:
    """Evaluates vehicle condition based on VIN, description, and mileage."""

    async def evaluate(
        self,
        make: str,
        model: str,
        year: int | None,
        vin: str,
        mileage: int,
        condition_description: str,
    ) -> dict[str, Any]:
        """
        Evaluate vehicle condition using LLM-powered assessment.

        Args:
            make: Vehicle make
            model: Vehicle model
            year: Vehicle year
            vin: Vehicle Identification Number
            mileage: Current mileage
            condition_description: User-provided condition description

        Returns:
            Dictionary with condition_score, condition_notes, and recommended_inspection
        """
        if not llm_client.is_available():
            logger.warning("LLM client not available for vehicle condition assessment")
            return self._fallback_assessment()

        try:
            assessment_result = generate_structured_json(
                prompt_id="vehicle_condition",
                variables={
                    "make": make or "Unknown",
                    "model": model or "Unknown",
                    "year": str(year) if year else "Unknown",
                    "vin": vin,
                    "mileage": mileage,
                    "condition_description": condition_description or "Not provided",
                },
                response_model=VehicleConditionAssessment,
                temperature=0.7,
                agent_role="evaluator",
            )

            logger.info(
                f"Vehicle condition assessment completed successfully. "
                f"Score: {assessment_result.condition_score}/10"
            )

            return {
                "condition_score": assessment_result.condition_score,
                "condition_notes": assessment_result.condition_notes,
                "recommended_inspection": assessment_result.recommended_inspection,
            }

        except Exception as e:
            logger.error(
                f"LLM evaluation error for vehicle condition: {type(e).__name__}: {e}. "
                f"VIN: {vin}. Using fallback assessment."
            )
            logger.exception("Full traceback for vehicle condition evaluation error:")
            return self._fallback_assessment()

    def _fallback_assessment(self) -> dict[str, Any]:
        """
        Provide fallback assessment when LLM is unavailable.

        Returns:
            Basic assessment dictionary with default values
        """
        return {
            "condition_score": 7.0,
            "condition_notes": ["Unable to perform detailed analysis. LLM service required."],
            "recommended_inspection": True,
        }

    def get_mileage_assessment(self, mileage: int) -> tuple[str, float]:
        """
        Get mileage assessment and scoring adjustment.

        Args:
            mileage: Vehicle mileage in miles

        Returns:
            Tuple of (assessment_text, score_adjustment)
        """
        if mileage < EvaluationConfig.MILEAGE_EXCEPTIONALLY_LOW:
            return "exceptionally low mileage", EvaluationConfig.MILEAGE_EXCEPTIONALLY_LOW_BONUS
        elif mileage < EvaluationConfig.MILEAGE_LOW:
            return "low mileage", EvaluationConfig.MILEAGE_LOW_BONUS
        elif mileage < EvaluationConfig.MILEAGE_MODERATE:
            return "moderate mileage", 0.0
        elif mileage < EvaluationConfig.MILEAGE_HIGH:
            return "high mileage", EvaluationConfig.MILEAGE_HIGH_PENALTY
        else:
            return "very high mileage", EvaluationConfig.MILEAGE_VERY_HIGH_PENALTY

    def get_condition_adjustment(self, condition: str) -> float:
        """
        Get scoring adjustment based on condition description.

        Args:
            condition: Condition description string

        Returns:
            Score adjustment value
        """
        condition_lower = condition.lower()
        if "excellent" in condition_lower or "like new" in condition_lower:
            return EvaluationConfig.CONDITION_EXCELLENT_BONUS
        elif "very good" in condition_lower or "good" in condition_lower:
            return EvaluationConfig.CONDITION_VERY_GOOD_BONUS
        elif "fair" in condition_lower:
            return EvaluationConfig.CONDITION_FAIR_PENALTY
        elif "poor" in condition_lower:
            return EvaluationConfig.CONDITION_POOR_PENALTY
        return 0.0
