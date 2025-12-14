"""
Deal Evaluation Service
Provides fair market value analysis and negotiation insights for vehicle deals
"""

import json
import logging
from typing import Any

from langchain.schema import HumanMessage, SystemMessage

from app.services.langchain_service import langchain_service

logger = logging.getLogger(__name__)


class DealEvaluationService:
    """Service for evaluating car deals and providing negotiation insights"""

    MAX_INSIGHTS = 5  # Maximum number of insights/talking points to return

    SYSTEM_PROMPT = """You are an expert automotive pricing analyst and negotiation advisor.

Your role is to:
1. Analyze vehicle pricing based on VIN, condition, mileage, and asking price
2. Provide fair market value estimates
3. Score deal quality on a 1-10 scale
4. Generate actionable negotiation insights
5. Identify key talking points for price negotiation

Be objective, data-driven, and provide specific, actionable recommendations."""

    async def evaluate_deal(
        self, vehicle_vin: str, asking_price: float, condition: str, mileage: int
    ) -> dict[str, Any]:
        """
        Evaluate a car deal and provide comprehensive analysis

        Args:
            vehicle_vin: 17-character Vehicle Identification Number
            asking_price: Asking price in USD
            condition: Vehicle condition description
            mileage: Current mileage in miles

        Returns:
            Dictionary containing fair_value, score, insights, and talking_points
        """
        # Check if LangChain service is available
        if not langchain_service.llm:
            return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)

        # Build analysis prompt
        prompt = f"""Analyze this vehicle deal and provide a comprehensive evaluation:

Vehicle Details:
- VIN: {vehicle_vin}
- Asking Price: ${asking_price:,.2f}
- Condition: {condition}
- Mileage: {mileage:,} miles

Provide a JSON response with EXACTLY this structure:
{{
  "fair_value": 25000.00,
  "score": 7.5,
  "insights": [
    "This vehicle is priced $X above/below market value",
    "The mileage is average/high/low for this year",
    "Condition rating suggests proper maintenance"
  ],
  "talking_points": [
    "Point out comparable vehicles priced at $X",
    "Mention the above-average mileage as negotiation leverage",
    "Request maintenance records to justify the condition rating"
  ]
}}

Requirements:
- fair_value: Estimated fair market value in USD (numeric)
- score: Deal quality score from 1-10 (1=terrible deal, 10=excellent deal)
- insights: 3-5 key observations about the deal
- talking_points: 3-5 specific negotiation strategies

Be specific with dollar amounts and data points. Base your analysis on industry standards."""

        try:
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await langchain_service.llm.ainvoke(messages)
            llm_output = response.content

            # Ensure we have a string response
            if not isinstance(llm_output, str):
                logger.warning(f"Unexpected LLM response type: {type(llm_output)}")
                return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)

            # Parse LLM response - extract JSON from markdown code blocks if present
            if "```json" in llm_output:
                json_start = llm_output.find("```json") + 7
                json_end = llm_output.find("```", json_start)
                if json_end != -1:
                    llm_output = llm_output[json_start:json_end].strip()
            elif "```" in llm_output:
                json_start = llm_output.find("```") + 3
                json_end = llm_output.find("```", json_start)
                if json_end != -1:
                    llm_output = llm_output[json_start:json_end].strip()

            # Parse JSON response
            try:
                evaluation_data = json.loads(llm_output)
            except json.JSONDecodeError as parse_error:
                logger.error(f"Failed to parse LLM JSON response: {parse_error}")
                logger.debug(f"LLM output: {llm_output}")
                return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)

            # Validate and normalize the response
            return {
                "fair_value": float(evaluation_data.get("fair_value", asking_price * 0.95)),
                "score": max(1.0, min(10.0, float(evaluation_data.get("score", 5.0)))),
                "insights": evaluation_data.get("insights", [])[: self.MAX_INSIGHTS],
                "talking_points": evaluation_data.get("talking_points", [])[: self.MAX_INSIGHTS],
            }

        except Exception as e:
            logger.error(f"Deal evaluation error: {e}")
            return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)

    def _fallback_evaluation(
        self, vehicle_vin: str, asking_price: float, condition: str, mileage: int
    ) -> dict[str, Any]:
        """
        Fallback evaluation logic when LLM is not available

        Uses simple heuristics to provide basic evaluation
        """
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

        return {
            "fair_value": round(fair_value, 2),
            "score": round(score, 1),
            "insights": insights,
            "talking_points": talking_points,
        }


# Singleton instance
deal_evaluation_service = DealEvaluationService()
