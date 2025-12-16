"""
Deal Evaluation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.evaluation import EvaluationStatus, PipelineStep
from app.models.models import User
from app.repositories.deal_repository import DealRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.schemas.evaluation_schemas import (
    EvaluationAnswerRequest,
    EvaluationInitiateRequest,
    EvaluationResponse,
)
from app.services.deal_evaluation_service import deal_evaluation_service

router = APIRouter()


@router.post(
    "/{deal_id}/evaluation",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def initiate_or_continue_evaluation(
    deal_id: int,
    request: EvaluationInitiateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start a new evaluation or continue an existing one for a deal

    If an evaluation is in progress (awaiting_input), it will be continued with provided answers.
    Otherwise, a new evaluation will be started.
    """
    # Verify deal exists
    deal_repo = DealRepository(db)
    deal = deal_repo.get(deal_id)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Deal with id {deal_id} not found"
        )

    eval_repo = EvaluationRepository(db)

    # Check for existing evaluation in progress
    existing_eval = eval_repo.get_latest_by_deal(deal_id)

    if existing_eval and existing_eval.status != EvaluationStatus.COMPLETED:
        # Continue existing evaluation
        evaluation = existing_eval
    else:
        # Create new evaluation
        evaluation = eval_repo.create(
            user_id=current_user.id,
            deal_id=deal_id,
            status=EvaluationStatus.ANALYZING,
            current_step=PipelineStep.VEHICLE_CONDITION,
        )

    # Process the current step
    try:
        step_result = await deal_evaluation_service.process_evaluation_step(
            db=db, evaluation_id=evaluation.id, user_answers=request.answers
        )

        # Refresh evaluation to get updated state
        db.refresh(evaluation)

        return {
            "evaluation_id": evaluation.id,
            "deal_id": deal_id,
            "status": evaluation.status.value,
            "current_step": evaluation.current_step.value,
            "step_result": step_result,
            "result_json": evaluation.result_json,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing evaluation: {str(e)}",
        )


@router.get(
    "/{deal_id}/evaluation/{evaluation_id}",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
)
def get_evaluation(
    deal_id: int,
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the current state of a deal evaluation
    """
    eval_repo = EvaluationRepository(db)
    evaluation = eval_repo.get(evaluation_id)

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {evaluation_id} not found",
        )

    # Verify evaluation belongs to the deal
    if evaluation.deal_id != deal_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Evaluation {evaluation_id} does not belong to deal {deal_id}",
        )

    return evaluation


@router.post(
    "/{deal_id}/evaluation/{evaluation_id}/answers",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def submit_evaluation_answers(
    deal_id: int,
    evaluation_id: int,
    request: EvaluationAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit answers to evaluation questions and continue the pipeline
    """
    eval_repo = EvaluationRepository(db)
    evaluation = eval_repo.get(evaluation_id)

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {evaluation_id} not found",
        )

    # Verify evaluation belongs to the deal
    if evaluation.deal_id != deal_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Evaluation {evaluation_id} does not belong to deal {deal_id}",
        )

    # Verify evaluation is awaiting input
    if evaluation.status != EvaluationStatus.AWAITING_INPUT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Evaluation is not awaiting input. Current status: {evaluation.status.value}",
        )

    # Process with answers
    try:
        # Update status back to analyzing
        eval_repo.update_status(evaluation_id, EvaluationStatus.ANALYZING)

        step_result = await deal_evaluation_service.process_evaluation_step(
            db=db, evaluation_id=evaluation.id, user_answers=request.answers
        )

        # Refresh evaluation
        db.refresh(evaluation)

        return {
            "evaluation_id": evaluation.id,
            "deal_id": deal_id,
            "status": evaluation.status.value,
            "current_step": evaluation.current_step.value,
            "step_result": step_result,
            "result_json": evaluation.result_json,
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing answers: {str(e)}",
        )
