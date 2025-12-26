"""Test evaluation repository"""

import pytest

from app.models.evaluation import EvaluationStatus, PipelineStep
from app.models.models import Deal, User
from app.repositories.evaluation_repository import EvaluationRepository


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
def mock_deal(db):
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
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


def test_create_evaluation(db, mock_user, mock_deal):
    """Test creating a deal evaluation"""
    repo = EvaluationRepository(db)

    evaluation = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    assert evaluation.id is not None
    assert evaluation.user_id == mock_user.id
    assert evaluation.deal_id == mock_deal.id
    assert evaluation.status == EvaluationStatus.ANALYZING
    assert evaluation.current_step == PipelineStep.VEHICLE_CONDITION
    assert evaluation.result_json is None
    assert evaluation.created_at is not None


def test_get_evaluation(db, mock_user, mock_deal):
    """Test getting an evaluation by ID"""
    repo = EvaluationRepository(db)

    evaluation = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    retrieved = repo.get(evaluation.id)
    assert retrieved is not None
    assert retrieved.id == evaluation.id
    assert retrieved.user_id == mock_user.id
    assert retrieved.deal_id == mock_deal.id


def test_get_nonexistent_evaluation(db):
    """Test getting a non-existent evaluation"""
    repo = EvaluationRepository(db)
    evaluation = repo.get(99999)
    assert evaluation is None


def test_get_by_deal(db, mock_user, mock_deal):
    """Test getting all evaluations for a deal"""
    repo = EvaluationRepository(db)

    # Create multiple evaluations
    eval1 = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    eval2 = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.COMPLETED,
        current_step=PipelineStep.FINAL,
    )

    evaluations = repo.get_by_deal(mock_deal.id)
    assert len(evaluations) == 2
    assert eval1.id in [e.id for e in evaluations]
    assert eval2.id in [e.id for e in evaluations]


def test_get_latest_by_deal(db, mock_user, mock_deal):
    """Test getting the most recent evaluation for a deal"""
    repo = EvaluationRepository(db)

    # Create multiple evaluations
    eval1 = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    eval2 = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.COMPLETED,
        current_step=PipelineStep.FINAL,
    )

    latest = repo.get_latest_by_deal(mock_deal.id)
    assert latest is not None
    # Should return one of the evaluations for this deal
    assert latest.id in [eval1.id, eval2.id]
    assert latest.deal_id == mock_deal.id


def test_get_by_user(db, mock_user, mock_deal):
    """Test getting all evaluations for a user"""
    repo = EvaluationRepository(db)

    # Create evaluations
    eval1 = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    evaluations = repo.get_by_user(mock_user.id)
    assert len(evaluations) >= 1
    assert eval1.id in [e.id for e in evaluations]


def test_update_status(db, mock_user, mock_deal):
    """Test updating evaluation status"""
    repo = EvaluationRepository(db)

    evaluation = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    updated = repo.update_status(evaluation.id, EvaluationStatus.AWAITING_INPUT)
    assert updated is not None
    assert updated.status == EvaluationStatus.AWAITING_INPUT


def test_update_step(db, mock_user, mock_deal):
    """Test updating evaluation step"""
    repo = EvaluationRepository(db)

    evaluation = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    updated = repo.update_step(evaluation.id, PipelineStep.PRICE)
    assert updated is not None
    assert updated.current_step == PipelineStep.PRICE


def test_update_result(db, mock_user, mock_deal):
    """Test updating evaluation result"""
    repo = EvaluationRepository(db)

    evaluation = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    result_data = {"vehicle_condition": {"score": 8.5, "notes": ["Good condition"]}}

    updated = repo.update_result(evaluation.id, result_data, EvaluationStatus.COMPLETED)
    assert updated is not None
    assert updated.result_json == result_data
    assert updated.status == EvaluationStatus.COMPLETED


def test_advance_step(db, mock_user, mock_deal):
    """Test advancing to next step"""
    repo = EvaluationRepository(db)

    evaluation = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    step_result = {"score": 8.5, "notes": ["Good condition"]}

    updated = repo.advance_step(evaluation.id, PipelineStep.PRICE, step_result)
    assert updated is not None
    assert updated.current_step == PipelineStep.PRICE
    assert updated.result_json is not None
    assert PipelineStep.VEHICLE_CONDITION.value in updated.result_json
    assert updated.result_json[PipelineStep.VEHICLE_CONDITION.value] == step_result


def test_delete_evaluation(db, mock_user, mock_deal):
    """Test deleting an evaluation"""
    repo = EvaluationRepository(db)

    evaluation = repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    evaluation_id = evaluation.id
    deleted = repo.delete(evaluation_id)
    assert deleted is True

    # Verify deletion
    retrieved = repo.get(evaluation_id)
    assert retrieved is None


def test_delete_nonexistent_evaluation(db):
    """Test deleting a non-existent evaluation"""
    repo = EvaluationRepository(db)
    deleted = repo.delete(99999)
    assert deleted is False
