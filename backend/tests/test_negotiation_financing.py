"""Tests for negotiation financing integration"""

import pytest

from app.models.models import Deal, DealStatus
from app.services.negotiation_service import NegotiationService


@pytest.fixture
def mock_deal(db):
    """Create a mock deal for testing"""
    deal = Deal(
        customer_name="John Doe",
        customer_email="john@example.com",
        vehicle_make="Toyota",
        vehicle_model="Camry",
        vehicle_year=2022,
        vehicle_mileage=15000,
        asking_price=25000.00,
        status=DealStatus.PENDING,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


class TestFinancingOptions:
    """Test financing options calculation in negotiation"""

    def test_calculate_financing_options_with_default_credit(self, db):
        """Test financing calculation with default credit score"""
        service = NegotiationService(db)
        vehicle_price = 30000.0

        financing_options = service._calculate_financing_options(vehicle_price)

        # Should return options for 36, 48, 60, 72 months
        assert len(financing_options) == 4

        # Check 60-month option exists
        option_60 = next((opt for opt in financing_options if opt["loan_term_months"] == 60), None)
        assert option_60 is not None
        assert option_60["loan_amount"] == 27000.0  # 90% of 30000
        assert option_60["down_payment"] == 3000.0  # 10% of 30000
        assert option_60["monthly_payment_estimate"] > 0
        assert option_60["total_cost"] > vehicle_price  # Total includes interest
        assert option_60["total_interest"] > 0

    def test_calculate_financing_options_excellent_credit(self, db):
        """Test financing calculation with excellent credit"""
        service = NegotiationService(db)
        vehicle_price = 25000.0

        financing_options = service._calculate_financing_options(
            vehicle_price, credit_score_range="excellent"
        )

        assert len(financing_options) == 4

        # Excellent credit should have lower APR
        option = financing_options[0]
        assert option["estimated_apr"] < 0.06  # Less than 6%

    def test_calculate_financing_options_poor_credit(self, db):
        """Test financing calculation with poor credit"""
        service = NegotiationService(db)
        vehicle_price = 20000.0

        financing_options = service._calculate_financing_options(
            vehicle_price, credit_score_range="poor"
        )

        assert len(financing_options) == 4

        # Poor credit should have higher APR
        option = financing_options[0]
        assert option["estimated_apr"] > 0.10  # Greater than 10%

    def test_calculate_financing_different_terms(self, db):
        """Test that different loan terms produce different payments"""
        service = NegotiationService(db)
        vehicle_price = 28000.0

        financing_options = service._calculate_financing_options(vehicle_price)

        # Get 36 and 72 month options
        option_36 = next((opt for opt in financing_options if opt["loan_term_months"] == 36), None)
        option_72 = next((opt for opt in financing_options if opt["loan_term_months"] == 72), None)

        assert option_36 is not None
        assert option_72 is not None

        # Shorter term should have higher monthly payment but lower total interest
        assert option_36["monthly_payment_estimate"] > option_72["monthly_payment_estimate"]
        assert option_36["total_interest"] < option_72["total_interest"]

    def test_financing_options_cash_savings_calculation(self, db):
        """Test cash savings calculation vs financing"""
        service = NegotiationService(db)
        vehicle_price = 25000.0

        financing_options = service._calculate_financing_options(vehicle_price)

        # Get baseline financing option (60 months)
        baseline = next((opt for opt in financing_options if opt["loan_term_months"] == 60), None)
        assert baseline is not None

        # Calculate cash savings
        cash_savings = baseline["total_cost"] - vehicle_price

        # Cash savings should be positive (total financed cost > cash price)
        assert cash_savings > 0

        # Cash savings should roughly equal total interest
        assert abs(cash_savings - baseline["total_interest"]) < 10  # Within $10


@pytest.mark.asyncio
async def test_negotiation_response_includes_financing(db, mock_deal):
    """Test that negotiation responses include financing options"""
    from unittest.mock import Mock, patch

    service = NegotiationService(db)

    # Mock the LLM response
    with patch(
        "app.services.negotiation_service.generate_text",
        return_value="Here's my offer for this vehicle.",
    ):
        response = await service._generate_agent_response(
            session=Mock(id=1, current_round=1, max_rounds=10),
            deal=mock_deal,
            user_target_price=22000.0,
            strategy="moderate",
            request_id="test-123",
        )

    # Check metadata includes financing options
    assert "metadata" in response
    metadata = response["metadata"]
    assert "financing_options" in metadata
    assert "cash_savings" in metadata

    # Verify financing options structure
    financing_options = metadata["financing_options"]
    assert isinstance(financing_options, list)
    assert len(financing_options) > 0

    # Check first option has required fields
    option = financing_options[0]
    assert "loan_amount" in option
    assert "down_payment" in option
    assert "monthly_payment_estimate" in option
    assert "loan_term_months" in option
    assert "estimated_apr" in option
    assert "total_cost" in option
    assert "total_interest" in option
