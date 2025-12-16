"""
Negotiation endpoints for multi-round negotiations
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.models import User
from app.schemas.negotiation_schemas import (
    CreateNegotiationRequest,
    NegotiationSessionResponse,
    NextRoundRequest,
)
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
