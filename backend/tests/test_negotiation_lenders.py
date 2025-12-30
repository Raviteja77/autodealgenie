"""Tests for negotiation lender recommendation endpoint"""

import pytest_asyncio

from app.models.models import Deal, DealStatus, User
from app.models.negotiation import MessageRole
from app.repositories.negotiation_repository import NegotiationRepository


@pytest_asyncio.fixture
async def mock_user(async_db):
    """Create a mock user for testing"""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="hashed",
        full_name="Test User",
    )
    async_db.add(user)
    await async_db.commit()
    await async_db.refresh(user)
    return user


@pytest_asyncio.fixture
async def mock_deal(async_db):
    """Create a mock deal for testing"""
    deal = Deal(
        customer_name="John Doe",
        customer_email="john@example.com",
        vehicle_make="Toyota",
        vehicle_vin="1HGCM41JXMN109186",
        vehicle_model="Camry",
        vehicle_year=2022,
        vehicle_mileage=15000,
        asking_price=25000.00,
        status=DealStatus.PENDING,
    )
    async_db.add(deal)
    await async_db.commit()
    await async_db.refresh(deal)
    return deal


@pytest_asyncio.fixture
async def mock_negotiation_session(async_db, mock_user, mock_deal):
    """Create a mock negotiation session"""
    repo = NegotiationRepository(async_db)
    session = await repo.create_session(user_id=mock_user.id, deal_id=mock_deal.id)

    # Add a message with suggested price
    await repo.add_message(
        session_id=session.id,
        role=MessageRole.AGENT,
        content="Here's a counter offer",
        round_number=1,
        metadata={"suggested_price": 22000.0, "asking_price": 25000.0},
    )

    return session


async def test_lender_service_integration(async_db, mock_negotiation_session, mock_deal):
    """Test that lender service returns recommendations based on negotiated price"""
    from app.schemas.loan_schemas import LenderRecommendationRequest
    from app.services.lender_service import LenderService

    # Calculate loan amount based on negotiated price (22000)
    negotiated_price = 22000.0
    down_payment = negotiated_price * 0.10
    loan_amount = negotiated_price - down_payment

    # Create request
    request = LenderRecommendationRequest(
        loan_amount=loan_amount,
        credit_score_range="good",
        loan_term_months=60,
    )

    # Get recommendations
    response = LenderService.get_recommendations(request, max_results=5)

    # Verify we got recommendations
    assert len(response.recommendations) > 0
    assert response.total_matches > 0

    # Verify first recommendation has required fields
    top_match = response.recommendations[0]
    assert top_match.rank == 1
    assert top_match.match_score > 0
    assert top_match.estimated_apr > 0
    assert top_match.estimated_monthly_payment > 0
    assert len(top_match.recommendation_reason) > 0

    # Verify lender info is complete
    assert top_match.lender.name
    assert top_match.lender.affiliate_url
    assert len(top_match.lender.features) > 0
    assert len(top_match.lender.benefits) > 0


async def test_lender_recommendations_different_credit_scores(async_db):
    """Test that better credit scores get better rates"""
    from app.schemas.loan_schemas import LenderRecommendationRequest
    from app.services.lender_service import LenderService

    loan_amount = 20000.0

    # Get recommendations for excellent credit
    excellent_request = LenderRecommendationRequest(
        loan_amount=loan_amount,
        credit_score_range="excellent",
        loan_term_months=60,
    )
    excellent_response = LenderService.get_recommendations(excellent_request, max_results=3)

    # Get recommendations for poor credit
    poor_request = LenderRecommendationRequest(
        loan_amount=loan_amount,
        credit_score_range="poor",
        loan_term_months=60,
    )
    poor_response = LenderService.get_recommendations(poor_request, max_results=3)

    # Both should have recommendations
    assert len(excellent_response.recommendations) > 0
    assert len(poor_response.recommendations) > 0

    # Excellent credit should have lower APR
    excellent_apr = excellent_response.recommendations[0].estimated_apr
    poor_apr = poor_response.recommendations[0].estimated_apr

    assert excellent_apr < poor_apr


async def test_lender_recommendations_ranking(async_db):
    """Test that lender recommendations are properly ranked"""
    from app.schemas.loan_schemas import LenderRecommendationRequest
    from app.services.lender_service import LenderService

    request = LenderRecommendationRequest(
        loan_amount=25000.0,
        credit_score_range="good",
        loan_term_months=60,
    )

    response = LenderService.get_recommendations(request, max_results=5)

    # Verify rankings are sequential
    assert len(response.recommendations) > 0
    for i, match in enumerate(response.recommendations, start=1):
        assert match.rank == i

    # Verify scores are in descending order
    scores = [match.match_score for match in response.recommendations]
    assert scores == sorted(scores, reverse=True)
