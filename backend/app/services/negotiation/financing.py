import logging
from typing import Any

from app.core.negotiation_config import NegotiationConfig
from app.services.loan_calculator_service import LoanCalculatorService

logger = logging.getLogger(__name__)


class FinancingCalculator:
    """Specialized logic for calculating financing and cash savings during negotiation rounds."""

    @staticmethod
    def calculate_financing_options(
        vehicle_price: float, credit_score_range: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Calculate multiple financing options for different loan terms

        Args:
            vehicle_price: Current negotiated vehicle price
            credit_score_range: Credit score range (defaults to 'good')

        Returns:
            List of financing option dictionaries
        """
        if credit_score_range is None:
            credit_score_range = NegotiationConfig.DEFAULT_CREDIT_SCORE_RANGE

        # Calculate down payment (10% of price)
        down_payment = vehicle_price * NegotiationConfig.DEFAULT_DOWN_PAYMENT_PERCENT

        # Common loan terms to calculate (in months)
        loan_terms = [36, 48, 60, 72]
        financing_options = []

        for term_months in loan_terms:
            try:
                # Calculate loan details using LoanCalculatorService
                loan_result = LoanCalculatorService.calculate_loan(
                    loan_amount=vehicle_price,
                    down_payment=down_payment,
                    loan_term_months=term_months,
                    credit_score_range=credit_score_range,
                    include_amortization=False,
                )

                financing_options.append(
                    {
                        "loan_amount": loan_result.principal,
                        "down_payment": loan_result.down_payment,
                        "monthly_payment_estimate": loan_result.monthly_payment,
                        "loan_term_months": loan_result.loan_term_months,
                        "estimated_apr": loan_result.apr,
                        "total_cost": loan_result.total_amount + loan_result.down_payment,
                        "total_interest": loan_result.total_interest,
                    }
                )
            except ValueError as e:
                logger.warning(
                    f"Failed to calculate financing for {term_months} month term: {str(e)}"
                )
                continue
            except Exception as e:
                logger.exception(
                    f"Unexpected error calculating financing for {term_months} month term: {str(e)}"
                )
                # Continue to try other terms rather than failing completely
                continue

        return financing_options
