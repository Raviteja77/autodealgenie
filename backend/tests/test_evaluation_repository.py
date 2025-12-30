"""Test evaluation repository"""

import pytest_asyncio

from app.models.evaluation import EvaluationStatus, PipelineStep
from app.models.models import Deal, User
from app.repositories.evaluation_repository import EvaluationRepository


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
    )
    async_db.add(deal)
    await async_db.commit()
    await async_db.refresh(deal)
    return deal


async def test_create_evaluation(async_db, mock_user, mock_deal):
    """Test creating a deal evaluation"""
    repo = EvaluationRepository(async_db)

    evaluation = await repo.create(
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


async def test_get_evaluation(async_db, mock_user, mock_deal):
    """Test getting an evaluation by ID"""
    repo = EvaluationRepository(async_db)

    evaluation = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    retrieved = await repo.get(evaluation.id)
    assert retrieved is not None
    assert retrieved.id == evaluation.id
    assert retrieved.user_id == mock_user.id
    assert retrieved.deal_id == mock_deal.id


async def test_get_nonexistent_evaluation(async_db):
    """Test getting a non-existent evaluation"""
    repo = EvaluationRepository(async_db)
    evaluation = await repo.get(99999)
    assert evaluation is None


async def test_get_by_deal(async_db, mock_user, mock_deal):
    """Test getting all evaluations for a deal"""
    repo = EvaluationRepository(async_db)

    # Create multiple evaluations
    eval1 = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    eval2 = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.COMPLETED,
        current_step=PipelineStep.FINAL,
    )

    evaluations = await repo.get_by_deal(mock_deal.id)
    assert len(evaluations) == 2
    assert eval1.id in [e.id for e in evaluations]
    assert eval2.id in [e.id for e in evaluations]


async def test_get_latest_by_deal(async_db, mock_user, mock_deal):
    """Test getting the most recent evaluation for a deal"""
    repo = EvaluationRepository(async_db)

    # Create multiple evaluations
    eval1 = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    eval2 = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.COMPLETED,
        current_step=PipelineStep.FINAL,
    )

    latest = await repo.get_latest_by_deal(mock_deal.id)
    assert latest is not None
    # Should return one of the evaluations for this deal
    assert latest.id in [eval1.id, eval2.id]
    assert latest.deal_id == mock_deal.id


async def test_get_by_user(async_db, mock_user, mock_deal):
    """Test getting all evaluations for a user"""
    repo = EvaluationRepository(async_db)

    # Create evaluations
    eval1 = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    evaluations = await repo.get_by_user(mock_user.id)
    assert len(evaluations) >= 1
    assert eval1.id in [e.id for e in evaluations]


async def test_update_status(async_db, mock_user, mock_deal):
    """Test updating evaluation status"""
    repo = EvaluationRepository(async_db)

    evaluation = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    updated = await repo.update_status(evaluation.id, EvaluationStatus.AWAITING_INPUT)
    assert updated is not None
    assert updated.status == EvaluationStatus.AWAITING_INPUT


async def test_update_step(async_db, mock_user, mock_deal):
    """Test updating evaluation step"""
    repo = EvaluationRepository(async_db)

    evaluation = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    updated = await repo.update_step(evaluation.id, PipelineStep.PRICE)
    assert updated is not None
    assert updated.current_step == PipelineStep.PRICE


async def test_update_result(async_db, mock_user, mock_deal):
    """Test updating evaluation result"""
    repo = EvaluationRepository(async_db)

    evaluation = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    result_data = {"vehicle_condition": {"score": 8.5, "notes": ["Good condition"]}}

    updated = await repo.update_result(evaluation.id, result_data, EvaluationStatus.COMPLETED)
    assert updated is not None
    assert updated.result_json == result_data
    assert updated.status == EvaluationStatus.COMPLETED


async def test_advance_step(async_db, mock_user, mock_deal):
    """Test advancing to next step"""
    repo = EvaluationRepository(async_db)

    evaluation = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    step_result = {"score": 8.5, "notes": ["Good condition"]}

    updated = await repo.advance_step(evaluation.id, PipelineStep.PRICE, step_result)
    assert updated is not None
    assert updated.current_step == PipelineStep.PRICE
    assert updated.result_json is not None
    assert PipelineStep.VEHICLE_CONDITION.value in updated.result_json
    assert updated.result_json[PipelineStep.VEHICLE_CONDITION.value] == step_result


async def test_delete_evaluation(async_db, mock_user, mock_deal):
    """Test deleting an evaluation"""
    repo = EvaluationRepository(async_db)

    evaluation = await repo.create(
        user_id=mock_user.id,
        deal_id=mock_deal.id,
        status=EvaluationStatus.ANALYZING,
        current_step=PipelineStep.VEHICLE_CONDITION,
    )

    evaluation_id = evaluation.id
    deleted = await repo.delete(evaluation_id)
    assert deleted is True

    # Verify deletion
    retrieved = await repo.get(evaluation_id)
    assert retrieved is None


async def test_delete_nonexistent_evaluation(async_db):
    """Test deleting a non-existent evaluation"""
    repo = EvaluationRepository(async_db)
    deleted = await repo.delete(99999)
    assert deleted is False
