"""
Unit tests for Loan Calculator Service
"""

import pytest

from app.services.loan_calculator_service import (
    APR_RATES,
    CreditScoreRange,
    LoanCalculatorService,
)


class TestLoanCalculatorValidation:
    """Test input validation"""

    def test_validate_negative_loan_amount(self):
        """Test that negative loan amount raises ValueError"""
        with pytest.raises(ValueError, match="Loan amount must be greater than 0"):
            LoanCalculatorService.validate_inputs(-10000, 2000, 60, "good")

    def test_validate_zero_loan_amount(self):
        """Test that zero loan amount raises ValueError"""
        with pytest.raises(ValueError, match="Loan amount must be greater than 0"):
            LoanCalculatorService.validate_inputs(0, 2000, 60, "good")

    def test_validate_negative_down_payment(self):
        """Test that negative down payment raises ValueError"""
        with pytest.raises(ValueError, match="Down payment cannot be negative"):
            LoanCalculatorService.validate_inputs(25000, -1000, 60, "good")

    def test_validate_down_payment_exceeds_loan_amount(self):
        """Test that down payment >= loan amount raises ValueError"""
        with pytest.raises(ValueError, match="Down payment must be less than loan amount"):
            LoanCalculatorService.validate_inputs(25000, 25000, 60, "good")

        with pytest.raises(ValueError, match="Down payment must be less than loan amount"):
            LoanCalculatorService.validate_inputs(25000, 30000, 60, "good")

    def test_validate_zero_loan_term(self):
        """Test that zero loan term raises ValueError"""
        with pytest.raises(ValueError, match="Loan term must be greater than 0"):
            LoanCalculatorService.validate_inputs(25000, 5000, 0, "good")

    def test_validate_negative_loan_term(self):
        """Test that negative loan term raises ValueError"""
        with pytest.raises(ValueError, match="Loan term must be greater than 0"):
            LoanCalculatorService.validate_inputs(25000, 5000, -12, "good")

    def test_validate_excessive_loan_term(self):
        """Test that loan term > 360 months raises ValueError"""
        with pytest.raises(ValueError, match="Loan term cannot exceed 360 months"):
            LoanCalculatorService.validate_inputs(25000, 5000, 361, "good")

    def test_validate_invalid_credit_score_range(self):
        """Test that invalid credit score range raises ValueError"""
        with pytest.raises(ValueError, match="Invalid credit score range"):
            LoanCalculatorService.validate_inputs(25000, 5000, 60, "invalid")

    def test_validate_valid_inputs(self):
        """Test that valid inputs do not raise errors"""
        # Should not raise any exceptions
        LoanCalculatorService.validate_inputs(25000, 5000, 60, "good")
        LoanCalculatorService.validate_inputs(30000, 0, 48, "excellent")
        LoanCalculatorService.validate_inputs(15000, 3000, 36, "poor")


class TestCreditScoreAPR:
    """Test APR rates for different credit scores"""

    def test_get_apr_for_excellent_credit(self):
        """Test APR for excellent credit score"""
        apr = LoanCalculatorService.get_apr_for_credit_score("excellent")
        assert apr == APR_RATES[CreditScoreRange.EXCELLENT]
        assert apr == 0.049  # 4.9%

    def test_get_apr_for_good_credit(self):
        """Test APR for good credit score"""
        apr = LoanCalculatorService.get_apr_for_credit_score("good")
        assert apr == APR_RATES[CreditScoreRange.GOOD]
        assert apr == 0.074  # 7.4%

    def test_get_apr_for_fair_credit(self):
        """Test APR for fair credit score"""
        apr = LoanCalculatorService.get_apr_for_credit_score("fair")
        assert apr == APR_RATES[CreditScoreRange.FAIR]
        assert apr == 0.104  # 10.4%

    def test_get_apr_for_poor_credit(self):
        """Test APR for poor credit score"""
        apr = LoanCalculatorService.get_apr_for_credit_score("poor")
        assert apr == APR_RATES[CreditScoreRange.POOR]
        assert apr == 0.134  # 13.4%

    def test_get_apr_case_insensitive(self):
        """Test that credit score range is case-insensitive"""
        apr_lower = LoanCalculatorService.get_apr_for_credit_score("excellent")
        apr_upper = LoanCalculatorService.get_apr_for_credit_score("EXCELLENT")
        apr_mixed = LoanCalculatorService.get_apr_for_credit_score("ExCeLLeNt")

        assert apr_lower == apr_upper == apr_mixed

    def test_get_apr_invalid_defaults_to_good(self):
        """Test that invalid credit score defaults to good credit APR"""
        apr = LoanCalculatorService.get_apr_for_credit_score("invalid")
        assert apr == APR_RATES[CreditScoreRange.GOOD]


class TestMonthlyPaymentCalculation:
    """Test monthly payment calculations"""

    def test_calculate_monthly_payment_basic(self):
        """Test basic monthly payment calculation"""
        principal = 20000
        annual_rate = 0.05  # 5%
        term_months = 60

        payment = LoanCalculatorService.calculate_monthly_payment(
            principal, annual_rate, term_months
        )

        # Expected payment: ~$377.42
        assert 375 < payment < 380

    def test_calculate_monthly_payment_zero_interest(self):
        """Test monthly payment with 0% interest"""
        principal = 24000
        annual_rate = 0.0
        term_months = 48

        payment = LoanCalculatorService.calculate_monthly_payment(
            principal, annual_rate, term_months
        )

        # With 0% interest, payment should be principal / term
        expected = principal / term_months
        assert abs(payment - expected) < 0.01

    def test_calculate_monthly_payment_zero_principal(self):
        """Test monthly payment with zero principal"""
        payment = LoanCalculatorService.calculate_monthly_payment(0, 0.05, 60)
        assert payment == 0.0

    def test_calculate_monthly_payment_zero_term(self):
        """Test monthly payment with zero term"""
        payment = LoanCalculatorService.calculate_monthly_payment(20000, 0.05, 0)
        assert payment == 0.0

    def test_calculate_monthly_payment_high_interest(self):
        """Test monthly payment with high interest rate"""
        principal = 15000
        annual_rate = 0.20  # 20% (high risk loan)
        term_months = 36

        payment = LoanCalculatorService.calculate_monthly_payment(
            principal, annual_rate, term_months
        )

        # Payment should be higher than principal/term due to interest
        assert payment > (principal / term_months)


class TestLoanCalculation:
    """Test complete loan calculations"""

    def test_calculate_loan_excellent_credit(self):
        """Test loan calculation with excellent credit"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=30000,
            down_payment=5000,
            loan_term_months=60,
            credit_score_range="excellent",
            include_amortization=False,
        )

        assert result.principal == 25000  # 30000 - 5000
        assert result.down_payment == 5000
        assert result.loan_term_months == 60
        assert result.credit_score_range == "excellent"
        assert result.apr == 0.049
        assert result.monthly_payment > 0
        assert result.total_interest > 0
        assert result.total_amount > 25000  # Greater than principal due to interest
        assert result.amortization_schedule is None

    def test_calculate_loan_poor_credit(self):
        """Test loan calculation with poor credit"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=20000,
            down_payment=2000,
            loan_term_months=48,
            credit_score_range="poor",
            include_amortization=False,
        )

        assert result.principal == 18000
        assert result.credit_score_range == "poor"
        assert result.apr == 0.134  # Poor credit has higher APR

        # Poor credit should have higher monthly payment than excellent credit
        excellent_result = LoanCalculatorService.calculate_loan(
            loan_amount=20000,
            down_payment=2000,
            loan_term_months=48,
            credit_score_range="excellent",
        )
        assert result.monthly_payment > excellent_result.monthly_payment

    def test_calculate_loan_zero_down_payment(self):
        """Test loan calculation with zero down payment"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=25000,
            down_payment=0,
            loan_term_months=60,
            credit_score_range="good",
        )

        assert result.principal == 25000
        assert result.down_payment == 0
        assert result.monthly_payment > 0

    def test_calculate_loan_short_term(self):
        """Test loan calculation with short term (12 months)"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=12000,
            down_payment=2000,
            loan_term_months=12,
            credit_score_range="good",
        )

        assert result.loan_term_months == 12
        # Short term means higher monthly payment but less total interest
        assert result.monthly_payment > 800  # 10000 / 12 = 833.33 minimum

    def test_calculate_loan_long_term(self):
        """Test loan calculation with long term (84 months / 7 years)"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=35000,
            down_payment=5000,
            loan_term_months=84,
            credit_score_range="good",
        )

        assert result.loan_term_months == 84
        # Long term means lower monthly payment but more total interest
        assert result.total_interest > 5000

    def test_calculate_loan_total_accuracy(self):
        """Test that total amount equals monthly payment * term"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=30000,
            down_payment=5000,
            loan_term_months=60,
            credit_score_range="good",
        )

        calculated_total = result.monthly_payment * result.loan_term_months
        # Allow small rounding difference
        assert abs(result.total_amount - calculated_total) < 1.0

    def test_calculate_loan_interest_accuracy(self):
        """Test that total interest = total paid - principal"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=25000,
            down_payment=3000,
            loan_term_months=48,
            credit_score_range="fair",
        )

        expected_interest = result.total_amount - result.principal
        # Allow small rounding difference
        assert abs(result.total_interest - expected_interest) < 1.0


class TestAmortizationSchedule:
    """Test amortization schedule generation"""

    def test_generate_amortization_schedule_length(self):
        """Test that amortization schedule has correct number of entries"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=20000,
            down_payment=2000,
            loan_term_months=36,
            credit_score_range="good",
            include_amortization=True,
        )

        assert result.amortization_schedule is not None
        assert len(result.amortization_schedule) == 36

    def test_generate_amortization_schedule_structure(self):
        """Test that each amortization entry has correct structure"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=15000,
            down_payment=3000,
            loan_term_months=24,
            credit_score_range="excellent",
            include_amortization=True,
        )

        schedule = result.amortization_schedule
        assert schedule is not None

        for i, entry in enumerate(schedule, start=1):
            assert entry.month == i
            assert entry.payment > 0
            assert entry.principal >= 0
            assert entry.interest >= 0
            assert entry.balance >= 0
            # Payment should equal principal + interest (within rounding)
            assert abs(entry.payment - (entry.principal + entry.interest)) < 0.01

    def test_amortization_schedule_balance_decreases(self):
        """Test that balance decreases with each payment"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=25000,
            down_payment=5000,
            loan_term_months=48,
            credit_score_range="good",
            include_amortization=True,
        )

        schedule = result.amortization_schedule
        assert schedule is not None

        # First balance should be close to principal
        assert schedule[0].balance < result.principal

        # Balance should decrease monotonically
        for i in range(len(schedule) - 1):
            assert schedule[i + 1].balance < schedule[i].balance

    def test_amortization_schedule_final_balance_zero(self):
        """Test that final balance is zero"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=20000,
            down_payment=2000,
            loan_term_months=60,
            credit_score_range="fair",
            include_amortization=True,
        )

        schedule = result.amortization_schedule
        assert schedule is not None
        assert schedule[-1].balance == 0.0

    def test_amortization_schedule_interest_decreases(self):
        """Test that interest portion decreases over time"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=30000,
            down_payment=5000,
            loan_term_months=60,
            credit_score_range="good",
            include_amortization=True,
        )

        schedule = result.amortization_schedule
        assert schedule is not None

        # First payment should have higher interest than last
        assert schedule[0].interest > schedule[-1].interest

        # Interest should generally decrease (allowing for rounding)
        first_third_avg = sum(e.interest for e in schedule[:20]) / 20
        last_third_avg = sum(e.interest for e in schedule[-20:]) / 20
        assert first_third_avg > last_third_avg

    def test_amortization_schedule_principal_increases(self):
        """Test that principal portion increases over time"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=25000,
            down_payment=3000,
            loan_term_months=48,
            credit_score_range="good",
            include_amortization=True,
        )

        schedule = result.amortization_schedule
        assert schedule is not None

        # First payment should have lower principal than last
        assert schedule[0].principal < schedule[-1].principal

        # Principal should generally increase
        first_third_avg = sum(e.principal for e in schedule[:16]) / 16
        last_third_avg = sum(e.principal for e in schedule[-16:]) / 16
        assert last_third_avg > first_third_avg

    def test_amortization_schedule_total_matches(self):
        """Test that sum of schedule payments matches total amount"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=20000,
            down_payment=2000,
            loan_term_months=36,
            credit_score_range="excellent",
            include_amortization=True,
        )

        schedule = result.amortization_schedule
        assert schedule is not None

        total_from_schedule = sum(entry.payment for entry in schedule)
        # Allow small rounding difference
        assert abs(total_from_schedule - result.total_amount) < 1.0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_minimal_loan_amount(self):
        """Test with very small loan amount"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=1000,
            down_payment=100,
            loan_term_months=12,
            credit_score_range="good",
        )

        assert result.principal == 900
        assert result.monthly_payment > 0
        assert result.total_interest >= 0

    def test_large_loan_amount(self):
        """Test with large loan amount"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=100000,
            down_payment=20000,
            loan_term_months=72,
            credit_score_range="excellent",
        )

        assert result.principal == 80000
        assert result.monthly_payment > 1000
        assert result.total_interest > 1000

    def test_maximum_loan_term(self):
        """Test with maximum loan term (360 months / 30 years)"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=30000,
            down_payment=5000,
            loan_term_months=360,
            credit_score_range="good",
        )

        assert result.loan_term_months == 360
        assert result.monthly_payment > 0
        # Very long term means very high total interest
        assert result.total_interest > result.principal

    def test_rounding_consistency(self):
        """Test that all monetary values are properly rounded to 2 decimals"""
        result = LoanCalculatorService.calculate_loan(
            loan_amount=23456.78,
            down_payment=3456.78,
            loan_term_months=47,
            credit_score_range="fair",
            include_amortization=True,
        )

        # Check main values are rounded
        assert result.monthly_payment == round(result.monthly_payment, 2)
        assert result.total_interest == round(result.total_interest, 2)
        assert result.total_amount == round(result.total_amount, 2)

        # Check amortization entries are rounded
        if result.amortization_schedule:
            for entry in result.amortization_schedule:
                assert entry.payment == round(entry.payment, 2)
                assert entry.principal == round(entry.principal, 2)
                assert entry.interest == round(entry.interest, 2)
                assert entry.balance == round(entry.balance, 2)
