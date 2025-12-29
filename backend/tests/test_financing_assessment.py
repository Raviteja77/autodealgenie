"""Test financing assessment functionality"""

import pytest
import pytest_asyncio

from app.api.dependencies import get_current_user
from app.models.evaluation import EvaluationStatus, PipelineStep
from app.models.models import Deal, User
from tests.conftest import async_db


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


@pytest.fixture
def authenticated_client(client, mock_user):
    """Override the get_current_user dependency to return mock user"""
    from app.main import app

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides.clear()


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
    )
    async_db.add(deal)
    await async_db.commit()
    await async_db.refresh(deal)
    return deal


@pytest.mark.asyncio
async def test_financing_assessment_with_income(authenticated_client, mock_deal):
    """Test financing assessment includes affordability analysis when income is provided"""
    # Start evaluation
    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
    )
    assert response.status_code == 200
    evaluation_id = response.json()["evaluation_id"]

    # Navigate to financing step by providing required answers
    # Condition step
    answers = {
        "vin": "1HGBH41JXMN109186",
        "condition_description": "Excellent condition",
    }
    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation_id}/answers",
        json={"answers": answers},
    )
    assert response.status_code == 200

    # Continue to next step
    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
    )
    assert response.status_code == 200

    # Price step should auto-complete, continue
    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
    )
    assert response.status_code == 200

    # Should now be on financing step
    current_step = response.json()["current_step"]
    assert current_step == "financing"

    # Provide financing answers with income
    financing_answers = {
        "financing_type": "loan",
        "interest_rate": 5.0,
        "down_payment": 5000.0,
        "monthly_income": 6000.0,
    }
    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation_id}/answers",
        json={"answers": financing_answers},
    )
    assert response.status_code == 200

    # Check financing assessment includes new fields
    result_json = response.json()["result_json"]
    financing_assessment = result_json["financing"]["assessment"]

    assert "affordability_score" in financing_assessment
    assert "affordability_notes" in financing_assessment
    assert "recommendation" in financing_assessment
    assert "recommendation_reason" in financing_assessment
    assert "cash_vs_financing_savings" in financing_assessment

    # Verify affordability score is calculated
    assert financing_assessment["affordability_score"] > 0
    assert len(financing_assessment["affordability_notes"]) > 0


@pytest.mark.asyncio
async def test_financing_assessment_cash_purchase(authenticated_client, mock_deal):
    """Test financing assessment for cash purchase"""
    # Start and navigate to financing step
    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
    )
    evaluation_id = response.json()["evaluation_id"]

    # Skip to financing by providing all required answers
    answers = {
        "vin": "1HGBH41JXMN109186",
        "condition_description": "Excellent condition",
    }
    authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation_id}/answers",
        json={"answers": answers},
    )
    authenticated_client.post(f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None})
    authenticated_client.post(f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None})

    # Provide cash financing answer
    financing_answers = {"financing_type": "cash"}
    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation_id}/answers",
        json={"answers": financing_answers},
    )
    assert response.status_code == 200

    # Check cash assessment
    result_json = response.json()["result_json"]
    financing_assessment = result_json["financing"]["assessment"]

    assert financing_assessment["financing_type"] == "cash"
    assert financing_assessment["total_cost"] == mock_deal.asking_price
    assert financing_assessment["affordability_score"] == 10.0
    assert financing_assessment["recommendation"] in ["cash", "either"]


@pytest.mark.asyncio
async def test_get_lender_recommendations(authenticated_client, mock_deal, mock_user, db):
    """Test fetching lender recommendations for a good deal with financing"""
    from app.repositories.evaluation_repository import EvaluationRepository

    # Create an evaluation with completed financing step
    repo = EvaluationRepository(async_db)
    evaluation = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.FINANCING,
    )

    # Mock result_json with completed financing and good deal score
    result_json = {
        "user_inputs": {
            "financing_type": "loan",
            "interest_rate": 5.0,
        },
        "price": {
            "completed": True,
            "assessment": {
                "score": 8.0,  # Good deal
                "fair_value": 23000.0,
            },
        },
        "financing": {
            "completed": True,
            "assessment": {
                "financing_type": "loan",
                "loan_amount": 20000.0,
                "recommendation": "financing",
                "recommendation_reason": "Good deal with reasonable financing",
            },
        },
    }
    await repo.update_result(evaluation.id, result_json, EvaluationStatus.ANALYZING)

    # Fetch lender recommendations
    response = authenticated_client.get(
        f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation.id}/lenders"
    )

    assert response.status_code == 200
    data = response.json()

    assert "recommendations" in data
    assert "total_matches" in data
    assert isinstance(data["recommendations"], list)


@pytest.mark.asyncio
async def test_lender_recommendations_not_for_poor_deals(
    authenticated_client, mock_deal, mock_user, db
):
    """Test that lender recommendations are not provided for poor quality deals"""
    from app.repositories.evaluation_repository import EvaluationRepository

    repo = EvaluationRepository(async_db)
    evaluation = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.FINANCING,
    )

    # Mock result_json with completed financing but poor deal score
    result_json = {
        "user_inputs": {
            "financing_type": "loan",
            "interest_rate": 8.0,
        },
        "price": {
            "completed": True,
            "assessment": {
                "score": 4.0,  # Poor deal
                "fair_value": 20000.0,
            },
        },
        "financing": {
            "completed": True,
            "assessment": {
                "financing_type": "loan",
                "loan_amount": 20000.0,
                "recommendation": "cash",
                "recommendation_reason": "Deal quality is poor",
            },
        },
    }
    await repo.update_result(evaluation.id, result_json, EvaluationStatus.ANALYZING)

    # Fetch lender recommendations
    response = authenticated_client.get(
        f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation.id}/lenders"
    )

    assert response.status_code == 200
    data = response.json()

    # Should return empty recommendations due to poor deal quality
    assert data["total_matches"] == 0
    assert len(data["recommendations"]) == 0


@pytest.mark.asyncio
async def test_lender_recommendations_requires_completed_financing(
    authenticated_client, mock_deal, mock_user, db
):
    """Test that lender recommendations require completed financing step"""
    from app.repositories.evaluation_repository import EvaluationRepository

    repo = EvaluationRepository(async_db)
    evaluation = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.PRICE,
    )

    # Mock result_json without completed financing
    result_json = {
        "price": {
            "completed": True,
            "assessment": {"score": 8.0},
        },
        "financing": {
            "completed": False,  # Not completed
        },
    }
    await repo.update_result(evaluation.id, result_json, EvaluationStatus.ANALYZING)

    # Try to fetch lender recommendations
    response = authenticated_client.get(
        f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation.id}/lenders"
    )

    assert response.status_code == 400
    assert "financing evaluation step must be completed" in response.json()["detail"].lower()
