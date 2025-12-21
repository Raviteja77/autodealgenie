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
from app.schemas.loan_schemas import LenderRecommendationRequest, LenderRecommendationResponse
from app.services.deal_evaluation_service import deal_evaluation_service
from app.services.lender_service import LenderService

router = APIRouter()

# Interest rate to credit score mapping thresholds
EXCELLENT_CREDIT_RATE_THRESHOLD = 4.0
GOOD_CREDIT_RATE_THRESHOLD = 6.0
FAIR_CREDIT_RATE_THRESHOLD = 10.0

# Default financing parameters
DEFAULT_DOWN_PAYMENT_RATIO = 0.2  # 20% down payment (80% loan)
DEFAULT_INTEREST_RATE = 5.5

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing evaluation: {str(e)}",
        ) from e


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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing answers: {str(e)}",
        ) from e


@router.get(
    "/{deal_id}/evaluation/{evaluation_id}/lenders",
    response_model=LenderRecommendationResponse,
    status_code=status.HTTP_200_OK,
)
def get_evaluation_lenders(
    deal_id: int,
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get lender recommendations for a deal evaluation
    
    This endpoint analyzes the evaluation's financing assessment and provides
    personalized lender recommendations if the deal quality warrants financing.
    
    Returns lender recommendations only for deals with:
    - Completed financing evaluation step
    - Financing recommendation of "financing" or "either"
    - Overall deal score >= 6.5 (good or excellent deals)
    """
    eval_repo = EvaluationRepository(db)
    evaluation = eval_repo.get(evaluation_id)

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with id {evaluation_id} not found",
        )

    # Verify evaluation belongs to the current user
    if evaluation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this evaluation",
        )

    # Verify evaluation belongs to the deal
    if evaluation.deal_id != deal_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Evaluation {evaluation_id} does not belong to deal {deal_id}",
        )

    # Check if financing step is completed
    result_json = evaluation.result_json or {}
    financing_data = result_json.get("financing", {})
    
    if not financing_data.get("completed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Financing evaluation step must be completed before fetching lender recommendations",
        )

    financing_assessment = financing_data.get("assessment", {})
    
    # Check if financing is recommended
    recommendation = financing_assessment.get("recommendation", "")
    if recommendation not in ["financing", "either"]:
        # Return empty recommendations with explanation
        return LenderRecommendationResponse(
            recommendations=[],
            total_matches=0,
            request_summary={
                "message": f"Financing not recommended for this deal. Recommendation: {recommendation}",
                "reason": financing_assessment.get("recommendation_reason", ""),
            },
        )
    
    # Check overall deal quality
    final_data = result_json.get("final", {})
    overall_score = final_data.get("assessment", {}).get("overall_score", 0)
    
    # If final step not completed, estimate from price score
    if overall_score == 0:
        price_data = result_json.get("price", {})
        overall_score = price_data.get("assessment", {}).get("score", 0)
    
    min_score = deal_evaluation_service.LENDER_RECOMMENDATION_MIN_SCORE
    if overall_score < min_score:
        return LenderRecommendationResponse(
            recommendations=[],
            total_matches=0,
            request_summary={
                "message": "Deal quality is below threshold for lender recommendations",
                "overall_score": overall_score,
                "threshold": min_score,
            },
        )

    # Get deal information
    deal_repo = DealRepository(db)
    deal = deal_repo.get(deal_id)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deal with id {deal_id} not found",
        )

    # Extract financing parameters from user inputs
    user_inputs = result_json.get("user_inputs", {})
    loan_amount = financing_assessment.get("loan_amount", deal.asking_price * (1 - DEFAULT_DOWN_PAYMENT_RATIO))
    interest_rate = user_inputs.get("interest_rate", DEFAULT_INTEREST_RATE)
    
    # Estimate credit score range from interest rate (rough approximation)
    if interest_rate <= EXCELLENT_CREDIT_RATE_THRESHOLD:
        credit_score_range = "excellent"
    elif interest_rate <= GOOD_CREDIT_RATE_THRESHOLD:
        credit_score_range = "good"
    elif interest_rate <= FAIR_CREDIT_RATE_THRESHOLD:
        credit_score_range = "fair"
    else:
        credit_score_range = "poor"

    # Build lender recommendation request
    lender_request = LenderRecommendationRequest(
        loan_amount=loan_amount,
        credit_score_range=credit_score_range,
        loan_term_months=deal_evaluation_service.DEFAULT_LOAN_TERM_MONTHS,
    )

    # Get lender recommendations
    try:
        recommendations = LenderService.get_recommendations(lender_request, max_results=5)
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating lender recommendations: {str(e)}",
        ) from e
