"""
Financing Evaluator Module

Implements affordability metrics and payment-to-income calculations.
"""

import logging
from typing import Any

from app.core.evaluation_config import EvaluationConfig

logger = logging.getLogger(__name__)


class FinancingEvaluator:
    """Evaluates financing options and affordability metrics."""

    def evaluate(
        self,
        asking_price: float,
        financing_type: str,
        price_score: float,
        interest_rate: float | None = None,
        down_payment: float | None = None,
        monthly_income: float | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate financing and affordability.

        Args:
            asking_price: Vehicle asking price
            financing_type: Type of financing ('cash', 'loan', 'lease')
            price_score: Price evaluation score from pricing module
            interest_rate: Optional interest rate
            down_payment: Optional down payment amount
            monthly_income: Optional monthly income for affordability check

        Returns:
            Dictionary with financing assessment
        """
        logger.info(f"Evaluating financing: type={financing_type}, price=${asking_price:,.2f}")

        financing_type_lower = financing_type.lower()

        if financing_type_lower == "cash":
            return self._evaluate_cash(asking_price, price_score)
        else:
            return self._evaluate_loan(
                asking_price, price_score, interest_rate, down_payment, monthly_income
            )

    def _evaluate_cash(self, asking_price: float, price_score: float) -> dict[str, Any]:
        """
        Evaluate cash purchase.

        Args:
            asking_price: Vehicle asking price
            price_score: Price evaluation score

        Returns:
            Cash purchase assessment
        """
        affordability_notes = ["No monthly payments required", "No interest costs"]
        affordability_score = 10.0  # Best affordability for cash

        # Determine recommendation based on deal quality
        if price_score >= EvaluationConfig.GOOD_DEAL_SCORE:
            recommendation = "cash"
            recommendation_reason = (
                "This is a good deal - paying cash avoids interest and saves money long-term"
            )
        else:
            recommendation = "either"
            recommendation_reason = "Cash eliminates interest costs, but consider financing if you want to preserve liquidity"

        return {
            "financing_type": "cash",
            "monthly_payment": None,
            "total_cost": asking_price,
            "total_interest": None,
            "affordability_score": affordability_score,
            "affordability_notes": affordability_notes,
            "recommendation": recommendation,
            "recommendation_reason": recommendation_reason,
            "cash_vs_financing_savings": None,
        }

    def _evaluate_loan(
        self,
        asking_price: float,
        price_score: float,
        interest_rate: float | None,
        down_payment: float | None,
        monthly_income: float | None,
    ) -> dict[str, Any]:
        """
        Evaluate loan financing.

        Args:
            asking_price: Vehicle asking price
            price_score: Price evaluation score
            interest_rate: Interest rate (default 5.5%)
            down_payment: Down payment amount (default 20%)
            monthly_income: Monthly income for affordability check

        Returns:
            Loan financing assessment
        """
        # Use defaults if not provided
        if interest_rate is None:
            interest_rate = 5.5

        if down_payment is None:
            down_payment = asking_price * EvaluationConfig.DEFAULT_DOWN_PAYMENT_RATIO

        loan_amount = asking_price - down_payment

        # Calculate monthly payment
        monthly_rate = interest_rate / 100 / 12
        months = EvaluationConfig.DEFAULT_LOAN_TERM_MONTHS

        if monthly_rate > 0:
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** months) / (
                (1 + monthly_rate) ** months - 1
            )
        else:
            monthly_payment = loan_amount / months

        total_cost = down_payment + (monthly_payment * months)
        total_interest = total_cost - asking_price

        # Calculate affordability metrics
        affordability_notes = []
        affordability_score = 5.0  # Base score

        # Check payment-to-income ratio
        if monthly_income and monthly_income > 0:
            payment_ratio = (monthly_payment / monthly_income) * 100
            if payment_ratio <= EvaluationConfig.AFFORDABILITY_EXCELLENT:
                affordability_notes.append(
                    f"Excellent: Payment is {payment_ratio:.1f}% of monthly income"
                )
                affordability_score = 9.0
            elif payment_ratio <= EvaluationConfig.AFFORDABILITY_GOOD:
                affordability_notes.append(
                    f"Good: Payment is {payment_ratio:.1f}% of monthly income"
                )
                affordability_score = 7.0
            elif payment_ratio <= EvaluationConfig.AFFORDABILITY_MODERATE:
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
            interest_percent = (total_interest / asking_price) * 100
            if interest_percent > EvaluationConfig.HIGH_INTEREST_THRESHOLD:
                affordability_notes.append(
                    f"High interest cost: ${total_interest:,.0f} ({interest_percent:.1f}% of purchase price)"
                )
            else:
                affordability_notes.append(
                    f"Interest cost: ${total_interest:,.0f} over {months} months"
                )

        # Cash vs financing savings
        cash_savings = total_interest

        # Generate financing recommendation
        recommendation, recommendation_reason = self._generate_recommendation(
            price_score, interest_rate, total_interest, affordability_score
        )

        logger.info(
            f"Loan evaluation completed - Monthly: ${monthly_payment:.2f}, "
            f"Affordability Score: {affordability_score:.1f}/10"
        )

        return {
            "financing_type": "loan",
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

    def _generate_recommendation(
        self,
        price_score: float,
        interest_rate: float,
        total_interest: float,
        affordability_score: float,
    ) -> tuple[str, str]:
        """
        Generate financing recommendation based on multiple factors.

        Args:
            price_score: Price evaluation score
            interest_rate: Interest rate
            total_interest: Total interest to be paid
            affordability_score: Affordability score

        Returns:
            Tuple of (recommendation, reason)
        """
        if price_score >= EvaluationConfig.EXCELLENT_DEAL_SCORE:
            # Excellent deal
            if interest_rate <= EvaluationConfig.LOW_INTEREST_RATE:
                return (
                    "financing",
                    "Excellent deal with low interest rate - financing preserves cash for other investments",
                )
            else:
                return (
                    "either",
                    "Excellent deal, but moderate interest rate - consider your cash position",
                )
        elif price_score >= EvaluationConfig.GOOD_DEAL_SCORE:
            # Good deal
            if interest_rate <= EvaluationConfig.REASONABLE_INTEREST_RATE:
                return (
                    "financing",
                    "Good deal with reasonable rate - financing is a viable option",
                )
            else:
                return (
                    "cash",
                    f"Good deal but interest costs add ${total_interest:,.0f} - cash is better if available",
                )
        else:
            # Fair or poor deal
            reason = "Deal quality is mediocre - avoid paying interest on an overpriced vehicle"
            if affordability_score < 5.0:
                reason += ". Payment may also strain your budget."
            return "cash", reason
