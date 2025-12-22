"""
Negotiation endpoints for multi-round negotiations
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.loan_schemas import LenderRecommendationRequest, LenderRecommendationResponse
from app.schemas.negotiation_schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    CreateNegotiationRequest,
    DealerInfoRequest,
    DealerInfoResponse,
    NegotiationSessionResponse,
    NextRoundRequest,
)
from app.services.lender_service import LenderService
from app.services.negotiation_service import NegotiationService
from app.utils.error_handler import ApiError

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_negotiation(
    request: CreateNegotiationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new negotiation session

    Creates a negotiation session for a specific deal and seeds round 1
    with the user's input. Returns the initial agent response.

    **Request Body:**
    - `deal_id`: ID of the deal being negotiated
    - `user_target_price`: User's target price
    - `strategy`: Optional negotiation strategy (e.g., "aggressive", "moderate")

    **Returns:**
    - `session_id`: ID of the created session
    - `status`: Current session status
    - `current_round`: Current negotiation round
    - `agent_message`: Agent's initial response
    - `metadata`: Additional context (suggested price, etc.)

    **Requires authentication**
    """
    service = NegotiationService(db)
    result = await service.create_negotiation(
        user_id=current_user.id,
        deal_id=request.deal_id,
        user_target_price=request.user_target_price,
        strategy=request.strategy,
    )
    return result


@router.post("/{session_id}/next")
async def process_next_round(
    session_id: int,
    request: NextRoundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process the next round of negotiation

    Handles user actions (confirm, reject, counter) and generates the
    agent's response for the next negotiation round.

    **Path Parameters:**
    - `session_id`: ID of the negotiation session

    **Request Body:**
    - `user_action`: User's action ("confirm", "reject", or "counter")
    - `counter_offer`: Counter offer price (required if action is "counter")

    **Returns:**
    - `session_id`: ID of the session
    - `status`: Updated session status
    - `current_round`: Current negotiation round
    - `agent_message`: Agent's response
    - `metadata`: Additional context

    **Requires authentication**

    **Note:** The session must belong to the authenticated user.
    """
    service = NegotiationService(db)

    # Verify session belongs to user
    session = service.negotiation_repo.get_session(session_id)
    if not session:
        raise ApiError(status_code=404, message=f"Session {session_id} not found")

    if session.user_id != current_user.id:
        raise ApiError(
            status_code=403,
            message="You don't have permission to access this session",
        )

    result = await service.process_next_round(
        session_id=session_id,
        user_action=request.user_action.value,
        counter_offer=request.counter_offer,
    )
    return result


@router.get("/{session_id}", response_model=NegotiationSessionResponse)
def get_negotiation_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a negotiation session with full message history

    Returns the complete session state including all messages exchanged
    during the negotiation.

    **Path Parameters:**
    - `session_id`: ID of the negotiation session

    **Returns:**
    - Full session details with message history

    **Requires authentication**

    **Note:** The session must belong to the authenticated user.
    """
    service = NegotiationService(db)

    # Verify session belongs to user
    session = service.negotiation_repo.get_session(session_id)
    if not session:
        raise ApiError(status_code=404, message=f"Session {session_id} not found")

    if session.user_id != current_user.id:
        raise ApiError(
            status_code=403,
            message="You don't have permission to access this session",
        )

    result = service.get_session_with_messages(session_id)
    if not result:
        raise ApiError(status_code=404, message=f"Session {session_id} not found")

    return result


@router.get("/{session_id}/lender-recommendations", response_model=LenderRecommendationResponse)
def get_lender_recommendations(
    session_id: int,
    loan_term_months: int = 60,
    credit_score_range: str = "good",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get lender recommendations for a completed negotiation session

    Returns personalized lender recommendations based on the negotiated
    vehicle price and user's credit profile.

    **Path Parameters:**
    - `session_id`: ID of the negotiation session

    **Query Parameters:**
    - `loan_term_months`: Desired loan term (default: 60 months)
    - `credit_score_range`: Credit score range (excellent/good/fair/poor, default: good)

    **Returns:**
    - List of recommended lenders with estimated rates and payments
    - Total number of matching lenders
    - Request summary

    **Requires authentication**

    **Note:** The session must belong to the authenticated user and should
    ideally be completed to get the final negotiated price.
    """
    negotiation_service = NegotiationService(db)

    # Verify session belongs to user
    session = negotiation_service.negotiation_repo.get_session(session_id)
    if not session:
        raise ApiError(status_code=404, message=f"Session {session_id} not found")

    if session.user_id != current_user.id:
        raise ApiError(
            status_code=403,
            message="You don't have permission to access this session",
        )

    # Get the deal to determine the vehicle price
    deal = negotiation_service.deal_repo.get(session.deal_id)
    if not deal:
        raise ApiError(status_code=404, message="Associated deal not found")

    # Get the latest messages to find the final negotiated price
    messages = negotiation_service.negotiation_repo.get_messages(session_id)
    negotiated_price = deal.asking_price

    # Try to find the last suggested price in agent messages (check last 10 messages only)
    for msg in reversed(messages[-10:]):
        if msg.role.value == "agent" and msg.message_metadata:
            if "suggested_price" in msg.message_metadata:
                negotiated_price = msg.message_metadata["suggested_price"]
                break

    # Calculate down payment using shared constant
    from app.services.negotiation_service import NegotiationService

    down_payment = negotiated_price * NegotiationService.DEFAULT_DOWN_PAYMENT_PERCENT
    loan_amount = negotiated_price - down_payment

    # Create lender recommendation request
    lender_request = LenderRecommendationRequest(
        loan_amount=loan_amount,
        credit_score_range=credit_score_range,
        loan_term_months=loan_term_months,
    )

    # Get recommendations from lender service
    recommendations = LenderService.get_recommendations(lender_request, max_results=5)

    return recommendations


@router.post("/{session_id}/chat", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: int,
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a free-form chat message during negotiation

    Allows users to ask questions or discuss negotiation strategy
    without committing to specific actions (accept/reject/counter).

    **Path Parameters:**
    - `session_id`: ID of the negotiation session

    **Request Body:**
    - `message`: Chat message content (1-2000 characters)
    - `message_type`: Type of message (default: "general")

    **Returns:**
    - User message and AI agent's response

    **Requires authentication**

    **Note:** The session must belong to the authenticated user.
    """
    service = NegotiationService(db)

    # Verify session belongs to user
    session = service.negotiation_repo.get_session(session_id)
    if not session:
        raise ApiError(status_code=404, message=f"Session {session_id} not found")

    if session.user_id != current_user.id:
        raise ApiError(
            status_code=403,
            message="You don't have permission to access this session",
        )

    result = await service.send_chat_message(
        session_id=session_id,
        user_message=request.message,
        message_type=request.message_type,
    )
    return result


@router.post("/{session_id}/dealer-info", response_model=DealerInfoResponse)
async def submit_dealer_info(
    session_id: int,
    request: DealerInfoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit dealer-provided information for analysis

    Allows users to share information from the dealer (quotes, inspection
    reports, additional offers) and receive AI analysis and recommendations.

    **Path Parameters:**
    - `session_id`: ID of the negotiation session

    **Request Body:**
    - `info_type`: Type of dealer information
    - `content`: Dealer information content (1-5000 characters)
    - `price_mentioned`: Optional price from dealer info
    - `metadata`: Optional additional structured data

    **Returns:**
    - Analysis of dealer information and recommended actions

    **Requires authentication**

    **Note:** The session must belong to the authenticated user and be active.
    """
    service = NegotiationService(db)

    # Verify session belongs to user
    session = service.negotiation_repo.get_session(session_id)
    if not session:
        raise ApiError(status_code=404, message=f"Session {session_id} not found")

    if session.user_id != current_user.id:
        raise ApiError(
            status_code=403,
            message="You don't have permission to access this session",
        )

    result = await service.analyze_dealer_info(
        session_id=session_id,
        info_type=request.info_type,
        content=request.content,
        price_mentioned=request.price_mentioned,
        metadata=request.metadata,
    )
    return result
