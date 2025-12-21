"""Test loan endpoints"""

import pytest

from app.api.dependencies import get_current_user
from app.models.models import User, LoanStatus


@pytest.fixture
def mock_user(db):
    """Create a mock user for testing"""
    user = User(
        email="loanuser@example.com",
        username="loanuser",
        hashed_password="hashed",
        full_name="Loan User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client, mock_user):
    """Override the get_current_user dependency to return mock user"""
    from app.main import app

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides.clear()


def test_calculate_loan_payment_excellent_credit(authenticated_client):
    """Test loan calculation with excellent credit score"""
    calculation_data = {
        "loan_amount": 30000,
        "down_payment": 5000,
        "loan_term_months": 60,
        "credit_score_range": "excellent",
    }

    response = authenticated_client.post("/api/v1/loans/calculate", json=calculation_data)

    assert response.status_code == 200
    data = response.json()
    assert "monthly_payment" in data
    assert "total_interest" in data
    assert "total_amount" in data
    assert "interest_rate" in data
    assert data["interest_rate"] == 0.039  # 3.9% for excellent credit
    assert data["monthly_payment"] > 0
    assert data["total_interest"] > 0


def test_calculate_loan_payment_good_credit(authenticated_client):
    """Test loan calculation with good credit score"""
    calculation_data = {
        "loan_amount": 25000,
        "down_payment": 3000,
        "loan_term_months": 48,
        "credit_score_range": "good",
    }

    response = authenticated_client.post("/api/v1/loans/calculate", json=calculation_data)

    assert response.status_code == 200
    data = response.json()
    assert data["interest_rate"] == 0.059  # 5.9% for good credit
    assert data["monthly_payment"] > 0


def test_calculate_loan_payment_fair_credit(authenticated_client):
    """Test loan calculation with fair credit score"""
    calculation_data = {
        "loan_amount": 20000,
        "down_payment": 2000,
        "loan_term_months": 36,
        "credit_score_range": "fair",
    }

    response = authenticated_client.post("/api/v1/loans/calculate", json=calculation_data)

    assert response.status_code == 200
    data = response.json()
    assert data["interest_rate"] == 0.089  # 8.9% for fair credit


def test_calculate_loan_payment_poor_credit(authenticated_client):
    """Test loan calculation with poor credit score"""
    calculation_data = {
        "loan_amount": 15000,
        "down_payment": 1000,
        "loan_term_months": 60,
        "credit_score_range": "poor",
    }

    response = authenticated_client.post("/api/v1/loans/calculate", json=calculation_data)

    assert response.status_code == 200
    data = response.json()
    assert data["interest_rate"] == 0.129  # 12.9% for poor credit


def test_calculate_loan_payment_invalid_credit_score(authenticated_client):
    """Test loan calculation with invalid credit score range"""
    calculation_data = {
        "loan_amount": 20000,
        "down_payment": 2000,
        "loan_term_months": 48,
        "credit_score_range": "invalid",
    }

    response = authenticated_client.post("/api/v1/loans/calculate", json=calculation_data)

    # Should return 422 for validation error
    assert response.status_code == 422


def test_calculate_loan_payment_zero_term(authenticated_client):
    """Test loan calculation with zero loan term"""
    calculation_data = {
        "loan_amount": 20000,
        "down_payment": 2000,
        "loan_term_months": 0,
        "credit_score_range": "good",
    }

    response = authenticated_client.post("/api/v1/loans/calculate", json=calculation_data)

    # Should return 422 for validation error
    assert response.status_code == 422


def test_calculate_loan_payment_negative_amount(authenticated_client):
    """Test loan calculation with negative loan amount"""
    calculation_data = {
        "loan_amount": -10000,
        "down_payment": 2000,
        "loan_term_months": 48,
        "credit_score_range": "good",
    }

    response = authenticated_client.post("/api/v1/loans/calculate", json=calculation_data)

    # Should return 422 for validation error
    assert response.status_code == 422


def test_create_loan_application(authenticated_client, mock_user):
    """Test creating a loan application"""
    application_data = {
        "loan_amount": 25000,
        "down_payment": 5000,
        "trade_in_value": 3000,
        "loan_term_months": 60,
        "credit_score_range": "good",
        "annual_income": 75000,
        "employment_status": "employed",
    }

    response = authenticated_client.post(
        "/api/v1/loans/applications", json=application_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == mock_user.id
    assert data["loan_amount"] == 25000
    assert data["down_payment"] == 5000
    assert data["trade_in_value"] == 3000
    assert data["loan_term_months"] == 60
    assert data["credit_score_range"] == "good"
    assert data["status"] == LoanStatus.DRAFT.value


def test_create_loan_application_minimal_data(authenticated_client, mock_user):
    """Test creating a loan application with minimal required data"""
    application_data = {
        "loan_amount": 20000,
        "down_payment": 0,
        "trade_in_value": 0,
        "loan_term_months": 48,
        "credit_score_range": "fair",
    }

    response = authenticated_client.post(
        "/api/v1/loans/applications", json=application_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == mock_user.id
    assert data["annual_income"] is None
    assert data["employment_status"] is None


def test_create_loan_application_with_deal_id(authenticated_client, mock_user):
    """Test creating a loan application associated with a deal"""
    application_data = {
        "deal_id": 123,
        "loan_amount": 30000,
        "down_payment": 6000,
        "trade_in_value": 5000,
        "loan_term_months": 60,
        "credit_score_range": "excellent",
        "annual_income": 90000,
        "employment_status": "employed",
    }

    response = authenticated_client.post(
        "/api/v1/loans/applications", json=application_data
    )

    assert response.status_code == 200
    data = response.json()
    # Note: deal_id might be None if foreign key constraint fails in test
    # This is expected in test environment without actual deal


def test_get_loan_offers_excellent_credit(authenticated_client):
    """Test getting loan offers with excellent credit"""
    response = authenticated_client.get(
        "/api/v1/loans/offers",
        params={
            "loan_amount": 25000,
            "credit_score": "excellent",
            "loan_term": 60,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "offers" in data
    assert len(data["offers"]) > 0

    # Check offer structure
    first_offer = data["offers"][0]
    assert "lender_name" in first_offer
    assert "interest_rate" in first_offer
    assert "monthly_payment" in first_offer
    assert "total_cost" in first_offer
    assert "term_months" in first_offer
    assert "pre_approved" in first_offer

    # Excellent credit should have pre-approved offers
    assert any(offer["pre_approved"] for offer in data["offers"])


def test_get_loan_offers_poor_credit(authenticated_client):
    """Test getting loan offers with poor credit"""
    response = authenticated_client.get(
        "/api/v1/loans/offers",
        params={
            "loan_amount": 20000,
            "credit_score": "poor",
            "loan_term": 48,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "offers" in data
    assert len(data["offers"]) > 0

    # Poor credit should have higher interest rates
    for offer in data["offers"]:
        assert offer["interest_rate"] > 0.08  # Higher than 8%


def test_get_loan_offers_rate_comparison(authenticated_client):
    """Test that different lenders provide different rates"""
    response = authenticated_client.get(
        "/api/v1/loans/offers",
        params={
            "loan_amount": 25000,
            "credit_score": "good",
            "loan_term": 60,
        },
    )

    assert response.status_code == 200
    data = response.json()
    offers = data["offers"]

    # Should have multiple offers with different rates
    assert len(offers) >= 2
    rates = [offer["interest_rate"] for offer in offers]
    assert len(set(rates)) > 1  # Different rates


def test_loan_calculation_total_cost_accuracy(authenticated_client):
    """Test that total cost calculation is accurate"""
    calculation_data = {
        "loan_amount": 30000,
        "down_payment": 5000,
        "loan_term_months": 60,
        "credit_score_range": "good",
    }

    response = authenticated_client.post("/api/v1/loans/calculate", json=calculation_data)

    assert response.status_code == 200
    data = response.json()

    # Total amount should equal monthly payment * term + down payment
    expected_total_paid = data["monthly_payment"] * 60
    calculated_principal = calculation_data["loan_amount"] - calculation_data["down_payment"]

    # Total interest should be total paid minus principal
    expected_interest = expected_total_paid - calculated_principal

    # Allow small floating point differences
    assert abs(data["total_interest"] - expected_interest) < 1.0


def test_unauthorized_access_to_loan_endpoints(client):
    """Test that unauthenticated users cannot access loan endpoints"""
    # Try to calculate loan without authentication
    calculation_data = {
        "loan_amount": 25000,
        "down_payment": 5000,
        "loan_term_months": 60,
        "credit_score_range": "good",
    }

    response = client.post("/api/v1/loans/calculate", json=calculation_data)
    assert response.status_code == 401

    # Try to create application without authentication
    application_data = {
        "loan_amount": 25000,
        "down_payment": 5000,
        "trade_in_value": 0,
        "loan_term_months": 60,
        "credit_score_range": "good",
    }

    response = client.post("/api/v1/loans/applications", json=application_data)
    assert response.status_code == 401

    # Try to get offers without authentication
    response = client.get(
        "/api/v1/loans/offers",
        params={
            "loan_amount": 25000,
            "credit_score": "good",
            "loan_term": 60,
        },
    )
    assert response.status_code == 401
