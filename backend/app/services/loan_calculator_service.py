"""
Loan Calculator Service

Provides anonymous loan calculation functionality including:
- Monthly payment calculations
- Total interest calculations
- APR estimation based on credit score ranges
- Amortization schedule generation
"""

from enum import Enum

from pydantic import BaseModel, Field


class CreditScoreRange(str, Enum):
    """
    Credit score range categories with corresponding APR ranges.

    The ranges below show the typical APR spectrum for each credit tier.
    For calculations, we use the midpoint of each range to provide consistent,
    fair estimates. The ranges may overlap at boundaries, but each tier uses
    its own midpoint for calculations:
    - EXCELLENT: 3.9% - 5.9% → uses 4.9%
    - GOOD: 5.9% - 8.9% → uses 7.4%
    - FAIR: 8.9% - 11.9% → uses 10.4%
    - POOR: 11.9% - 14.9% → uses 13.4%
    """

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


# APR midpoints for each credit score range
APR_RATES = {
    CreditScoreRange.EXCELLENT: 0.049,  # 4.9%
    CreditScoreRange.GOOD: 0.074,  # 7.4%
    CreditScoreRange.FAIR: 0.104,  # 10.4%
    CreditScoreRange.POOR: 0.134,  # 13.4%
}


class AmortizationEntry(BaseModel):
    """Single entry in an amortization schedule"""

    month: int = Field(..., description="Payment month number")
    payment: float = Field(..., description="Total payment amount")
    principal: float = Field(..., description="Principal portion of payment")
    interest: float = Field(..., description="Interest portion of payment")
    balance: float = Field(..., description="Remaining balance after payment")


class LoanCalculationResult(BaseModel):
    """
    Complete loan calculation result with amortization schedule

    Note: Both interest_rate and apr fields are included for API compatibility.
    In this simplified calculator, they have the same value. In a production
    system, APR would include additional fees and costs beyond the interest rate.
    """

    monthly_payment: float = Field(..., description="Monthly payment amount")
    total_interest: float = Field(..., description="Total interest over loan term")
    total_amount: float = Field(..., description="Total amount paid over loan term")
    interest_rate: float = Field(..., description="Annual interest rate")
    apr: float = Field(
        ...,
        description="Annual Percentage Rate (same as interest_rate in this simplified calculator)",
    )
    principal: float = Field(..., description="Loan principal (after down payment)")
    down_payment: float = Field(..., description="Down payment amount")
    loan_term_months: int = Field(..., description="Loan term in months")
    credit_score_range: str = Field(..., description="Credit score range used")
    amortization_schedule: list[AmortizationEntry] | None = Field(
        None, description="Detailed payment schedule"
    )


class LoanCalculatorService:
    """Service for performing anonymous loan calculations"""

    @staticmethod
    def validate_inputs(
        loan_amount: float,
        down_payment: float,
        loan_term_months: int,
        credit_score_range: str,
    ) -> None:
        """
        Validate loan calculation inputs

        Args:
            loan_amount: Total loan amount (must be > 0)
            down_payment: Down payment amount (must be >= 0)
            loan_term_months: Loan term in months (must be > 0)
            credit_score_range: Credit score range category

        Raises:
            ValueError: If any input is invalid
        """
        if loan_amount <= 0:
            raise ValueError("Loan amount must be greater than 0")

        if down_payment < 0:
            raise ValueError("Down payment cannot be negative")

        if down_payment >= loan_amount:
            raise ValueError("Down payment must be less than loan amount")

        if loan_term_months <= 0:
            raise ValueError("Loan term must be greater than 0")

        if loan_term_months > 360:  # 30 years max
            raise ValueError("Loan term cannot exceed 360 months (30 years)")

        # Validate credit score range
        try:
            CreditScoreRange(credit_score_range.lower())
        except ValueError as e:
            valid_ranges = [r.value for r in CreditScoreRange]
            raise ValueError(
                f"Invalid credit score range. Must be one of: {', '.join(valid_ranges)}"
            ) from e

    @staticmethod
    def get_apr_for_credit_score(credit_score_range: str) -> float:
        """
        Get the APR midpoint for a given credit score range

        Args:
            credit_score_range: Credit score range category

        Returns:
            APR as a decimal (e.g., 0.049 for 4.9%)

        Note:
            This method is more forgiving than validate_inputs and defaults to 'good'
            credit for invalid inputs. This is intentional for use in mock loan offers
            where we want to provide a reasonable fallback rather than fail.
            For user-facing calculations, validate_inputs should be called first.
        """
        try:
            score_range = CreditScoreRange(credit_score_range.lower())
            return APR_RATES[score_range]
        except (ValueError, KeyError):
            # Default to good credit rate if invalid (for mock offers)
            return APR_RATES[CreditScoreRange.GOOD]

    @staticmethod
    def calculate_monthly_payment(
        principal: float, annual_rate: float, term_months: int
    ) -> float:
        """
        Calculate monthly payment using standard amortization formula

        Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        Where:
            M = Monthly payment
            P = Principal loan amount
            r = Monthly interest rate (annual rate / 12)
            n = Total number of payments (months)

        Args:
            principal: Loan principal amount
            annual_rate: Annual interest rate as decimal (e.g., 0.05 for 5%)
            term_months: Loan term in months

        Returns:
            Monthly payment amount
        """
        if principal <= 0:
            return 0.0

        if term_months <= 0:
            return 0.0

        monthly_rate = annual_rate / 12

        # Handle edge case where interest rate is 0
        if monthly_rate == 0:
            return principal / term_months

        # Standard amortization formula
        numerator = monthly_rate * ((1 + monthly_rate) ** term_months)
        denominator = ((1 + monthly_rate) ** term_months) - 1

        if denominator == 0:
            # Fallback for edge case
            return principal / term_months

        return principal * (numerator / denominator)

    @staticmethod
    def generate_amortization_schedule(
        principal: float,
        monthly_payment: float,
        annual_rate: float,
        term_months: int,
    ) -> list[AmortizationEntry]:
        """
        Generate detailed amortization schedule

        Args:
            principal: Loan principal amount
            monthly_payment: Monthly payment amount
            annual_rate: Annual interest rate as decimal
            term_months: Loan term in months

        Returns:
            List of amortization entries for each payment
        """
        schedule = []
        balance = principal
        monthly_rate = annual_rate / 12

        for month in range(1, term_months + 1):
            # Calculate interest for this month
            interest_payment = balance * monthly_rate

            # Calculate principal for this month
            principal_payment = monthly_payment - interest_payment

            # Adjust for final payment (handle rounding differences)
            if month == term_months:
                principal_payment = balance
                monthly_payment = principal_payment + interest_payment

            # Update balance
            balance -= principal_payment

            # Ensure balance doesn't go negative due to rounding
            if balance < 0.01:
                balance = 0.0

            schedule.append(
                AmortizationEntry(
                    month=month,
                    payment=round(monthly_payment, 2),
                    principal=round(principal_payment, 2),
                    interest=round(interest_payment, 2),
                    balance=round(balance, 2),
                )
            )

        return schedule

    @classmethod
    def calculate_loan(
        cls,
        loan_amount: float,
        down_payment: float,
        loan_term_months: int,
        credit_score_range: str,
        include_amortization: bool = False,
    ) -> LoanCalculationResult:
        """
        Calculate complete loan details including payments and interest

        Args:
            loan_amount: Total vehicle/loan amount
            down_payment: Down payment amount
            loan_term_months: Loan term in months
            credit_score_range: Credit score range category
            include_amortization: Whether to include full amortization schedule

        Returns:
            Complete loan calculation result

        Raises:
            ValueError: If inputs are invalid
        """
        # Validate all inputs
        cls.validate_inputs(
            loan_amount, down_payment, loan_term_months, credit_score_range
        )

        # Calculate principal (amount to be financed)
        principal = loan_amount - down_payment

        # Get APR for credit score range
        apr = cls.get_apr_for_credit_score(credit_score_range)

        # Calculate monthly payment
        monthly_payment = cls.calculate_monthly_payment(
            principal, apr, loan_term_months
        )

        # Calculate total amounts
        total_paid = monthly_payment * loan_term_months
        total_interest = total_paid - principal

        # Generate amortization schedule if requested
        amortization_schedule = None
        if include_amortization:
            amortization_schedule = cls.generate_amortization_schedule(
                principal, monthly_payment, apr, loan_term_months
            )

        return LoanCalculationResult(
            monthly_payment=round(monthly_payment, 2),
            total_interest=round(total_interest, 2),
            total_amount=round(total_paid, 2),
            interest_rate=apr,
            apr=apr,
            principal=round(principal, 2),
            down_payment=round(down_payment, 2),
            loan_term_months=loan_term_months,
            credit_score_range=credit_score_range.lower(),
            amortization_schedule=amortization_schedule,
        )
