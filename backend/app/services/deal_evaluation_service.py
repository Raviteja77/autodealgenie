"""
Deal Evaluation Service
Provides fair market value analysis and negotiation insights for vehicle deals
"""

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.llm import generate_structured_json, llm_client
from app.llm.schemas import DealEvaluation
from app.models.evaluation import EvaluationStatus, PipelineStep
from app.models.models import Deal
from app.repositories.evaluation_repository import EvaluationRepository

logger = logging.getLogger(__name__)


class DealEvaluationService:
    """Service for evaluating car deals and providing negotiation insights"""

    MAX_INSIGHTS = 5  # Maximum number of insights/talking points to return

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
        # Check if LLM client is available
        if not llm_client.is_available():
            return self._fallback_evaluation(vehicle_vin, asking_price, condition, mileage)

        try:
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

            # Convert Pydantic model to dict and ensure limits
            return {
                "fair_value": evaluation.fair_value,
                "score": evaluation.score,
                "insights": evaluation.insights[: self.MAX_INSIGHTS],
                "talking_points": evaluation.talking_points[: self.MAX_INSIGHTS],
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
        if langchain_service.llm:
            prompt = f"""Evaluate the vehicle condition for this deal:

Vehicle: {deal.vehicle_year} {deal.vehicle_make} {deal.vehicle_model}
VIN: {user_inputs.get('vin')}
Mileage: {deal.vehicle_mileage} miles
Condition Description: {user_inputs.get('condition_description')}

Provide a JSON response with:
{{
  "condition_score": 8.5,
  "condition_notes": ["Key observation 1", "Key observation 2"],
  "recommended_inspection": true
}}

Score should be 1-10 based on the description and mileage."""

            try:
                messages = [
                    SystemMessage(content=self.SYSTEM_PROMPT),
                    HumanMessage(content=prompt),
                ]
                response = await langchain_service.llm.ainvoke(messages)
                llm_output = response.content

                # Parse JSON from response
                if "```json" in llm_output:
                    json_start = llm_output.find("```json") + 7
                    json_end = llm_output.find("```", json_start)
                    if json_end != -1:
                        llm_output = llm_output[json_start:json_end].strip()

                assessment = json.loads(llm_output)
            except Exception as e:
                logger.error(f"LLM evaluation error: {e}")
                assessment = {
                    "condition_score": 7.0,
                    "condition_notes": ["Unable to perform detailed analysis"],
                    "recommended_inspection": True,
                }
        else:
            # Fallback assessment
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
        """Evaluate financing step"""
        user_inputs = result_json.get("user_inputs", {})

        # Check if financing information is provided
        if "financing_type" not in user_inputs:
            return {
                "questions": [
                    "What type of financing are you considering? (cash, loan, lease)",
                    "If financing, what is your estimated interest rate? (optional)",
                    "What is your planned down payment amount? (optional)",
                ],
                "required_fields": ["financing_type"],
            }

        financing_type = user_inputs.get("financing_type", "").lower()

        if financing_type == "cash":
            assessment = {
                "financing_recommendation": "Cash purchase eliminates interest costs",
                "estimated_total_cost": deal.asking_price,
            }
        else:
            interest_rate = user_inputs.get("interest_rate", 5.5)
            down_payment = user_inputs.get("down_payment", deal.asking_price * 0.2)
            loan_amount = deal.asking_price - down_payment
            # Simple 60-month loan calculation
            monthly_rate = interest_rate / 100 / 12
            months = 60
            if monthly_rate > 0:
                monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** months) / (
                    (1 + monthly_rate) ** months - 1
                )
            else:
                monthly_payment = loan_amount / months

            total_cost = down_payment + (monthly_payment * months)

            assessment = {
                "financing_type": financing_type,
                "loan_amount": round(loan_amount, 2),
                "estimated_monthly_payment": round(monthly_payment, 2),
                "estimated_total_cost": round(total_cost, 2),
                "total_interest": round(total_cost - deal.asking_price, 2),
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
                else "Moderate risk - proceed with caution"
                if risk_score < 7
                else "High risk - consider alternatives"
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
