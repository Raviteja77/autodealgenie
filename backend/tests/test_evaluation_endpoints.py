"""Test evaluation endpoints"""

import pytest

from app.api.dependencies import get_current_user
from app.models.evaluation import EvaluationStatus, PipelineStep
from app.models.models import Deal, User


@pytest.fixture
def mock_user(db):
    """Create a mock user for testing"""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password="hashed",
        full_name="Test User",
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
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


@pytest.mark.asyncio
async def test_initiate_evaluation(authenticated_client, mock_deal):
    """Test initiating a new evaluation"""
    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
    )

    assert response.status_code == 200
    data = response.json()
    assert "evaluation_id" in data
    assert data["deal_id"] == mock_deal.id
    assert data["status"] in [s.value for s in EvaluationStatus]
    assert data["current_step"] in [s.value for s in PipelineStep]


@pytest.mark.asyncio
async def test_initiate_evaluation_nonexistent_deal(authenticated_client):
    """Test initiating evaluation for non-existent deal"""
    response = authenticated_client.post("/api/v1/deals/99999/evaluation", json={"answers": None})

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_evaluation(authenticated_client, mock_deal):
    """Test getting an evaluation"""
    # First create an evaluation
    create_response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
    )
    assert create_response.status_code == 200
    evaluation_id = create_response.json()["evaluation_id"]

    # Now get the evaluation
    response = authenticated_client.get(f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == evaluation_id
    assert data["deal_id"] == mock_deal.id


def test_get_nonexistent_evaluation(authenticated_client, mock_deal):
    """Test getting a non-existent evaluation"""
    response = authenticated_client.get(f"/api/v1/deals/{mock_deal.id}/evaluation/99999")

    assert response.status_code == 404


def test_get_evaluation_wrong_deal(authenticated_client, mock_deal, db):
    """Test getting an evaluation for the wrong deal"""
    # Create another deal
    other_deal = Deal(
        customer_name="Jane Doe",
        customer_email="jane@example.com",
        vehicle_make="Honda",
        vehicle_model="Accord",
        vehicle_year=2021,
        vehicle_mileage=20000,
        asking_price=23000.00,
    )
    db.add(other_deal)
    db.commit()
    db.refresh(other_deal)

    # Create evaluation for original deal
    create_response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
    )
    evaluation_id = create_response.json()["evaluation_id"]

    # Try to get it with wrong deal_id
    response = authenticated_client.get(f"/api/v1/deals/{other_deal.id}/evaluation/{evaluation_id}")

    assert response.status_code == 400
    assert "does not belong" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_continue_evaluation_with_answers(authenticated_client, mock_deal):
    """Test continuing an evaluation with answers"""
    # Start evaluation
    create_response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
    )
    assert create_response.status_code == 200
    evaluation_id = create_response.json()["evaluation_id"]

    # Check if we need to provide answers
    step_result = create_response.json()["step_result"]

    if step_result.get("questions"):
        # Provide answers
        answers = {
            "vin": "1HGBH41JXMN109186",
            "condition_description": "Excellent condition, well maintained",
        }

        response = authenticated_client.post(
            f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation_id}/answers",
            json={"answers": answers},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["evaluation_id"] == evaluation_id


@pytest.mark.asyncio
async def test_submit_answers_when_not_awaiting(authenticated_client, mock_deal, db):
    """Test submitting answers when evaluation is not awaiting input"""
    from app.models.evaluation import DealEvaluation
    from app.repositories.evaluation_repository import EvaluationRepository

    # Create evaluation in completed status
    repo = EvaluationRepository(db)
    evaluation = repo.create(
        user_id=1,  # mock_user.id
        deal_id=mock_deal.id,
        status=EvaluationStatus.COMPLETED,
        current_step=PipelineStep.FINAL,
    )

    answers = {"test": "answer"}

    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation.id}/answers",
        json={"answers": answers},
    )

    assert response.status_code == 400
    assert "not awaiting input" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_full_evaluation_flow(authenticated_client, mock_deal):
    """Test a complete evaluation flow"""
    # Start evaluation
    response = authenticated_client.post(
        f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
    )
    assert response.status_code == 200

    evaluation_id = response.json()["evaluation_id"]
    current_status = response.json()["status"]

    # Continue providing answers until completed
    max_iterations = 10
    iteration = 0

    while current_status != "completed" and iteration < max_iterations:
        iteration += 1

        # Get current state
        get_response = authenticated_client.get(
            f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation_id}"
        )
        assert get_response.status_code == 200

        current_eval = get_response.json()
        current_status = current_eval["status"]

        if current_status == "awaiting_input":
            # Provide sample answers
            answers = {
                "vin": "1HGBH41JXMN109186",
                "condition_description": "Excellent condition",
                "financing_type": "cash",
            }

            answer_response = authenticated_client.post(
                f"/api/v1/deals/{mock_deal.id}/evaluation/{evaluation_id}/answers",
                json={"answers": answers},
            )
            assert answer_response.status_code == 200
            current_status = answer_response.json()["status"]
        elif current_status == "analyzing":
            # Continue evaluation
            continue_response = authenticated_client.post(
                f"/api/v1/deals/{mock_deal.id}/evaluation", json={"answers": None}
            )
            assert continue_response.status_code == 200
            current_status = continue_response.json()["status"]

    # Should reach completion within max iterations
    assert iteration < max_iterations
