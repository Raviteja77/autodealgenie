"""
Negotiation endpoints for multi-round negotiations
"""

import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.negotiation_config import NegotiationConfig
from app.db.session import get_async_db
from app.models.models import User
from app.schemas.loan_schemas import (
    LenderRecommendationRequest,
    LenderRecommendationResponse,
)
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
from app.services.negotiation import NegotiationService
from app.services.websocket_manager import connection_manager
from app.utils.error_handler import ApiError

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_negotiation(
    request: CreateNegotiationRequest,
    db: AsyncSession = Depends(get_async_db),
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
    - `evaluation_data`: Optional evaluation results (recommended for data-driven negotiation)

    **Returns:**
    - `session_id`: ID of the created session
    - `status`: Current session status
    - `current_round`: Current negotiation round
    - `agent_message`: Agent's initial response
    - `metadata`: Additional context (suggested price, evaluation data, etc.)

    **Requires authentication**
    """
    service = NegotiationService(db)
    result = await service.create_negotiation(
        user_id=current_user.id,
        deal_id=request.deal_id,
        user_target_price=request.user_target_price,
        strategy=request.strategy,
        evaluation_data=request.evaluation_data,
    )
    return result


@router.post("/{session_id}/next")
async def process_next_round(
    session_id: int,
    request: NextRoundRequest,
    db: AsyncSession = Depends(get_async_db),
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
    session = await service.negotiation_repo.get_session(session_id)
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
async def get_negotiation_session(
    session_id: int,
    db: AsyncSession = Depends(get_async_db),
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
    session = await service.negotiation_repo.get_session(session_id)
    if not session:
        raise ApiError(status_code=404, message=f"Session {session_id} not found")

    if session.user_id != current_user.id:
        raise ApiError(
            status_code=403,
            message="You don't have permission to access this session",
        )

    result = await service.get_session_with_messages(session_id)
    if not result:
        raise ApiError(status_code=404, message=f"Session {session_id} not found")

    return result


@router.get("/{session_id}/lender-recommendations", response_model=LenderRecommendationResponse)
async def get_lender_recommendations(
    session_id: int,
    loan_term_months: int = 60,
    credit_score_range: str = "good",
    db: AsyncSession = Depends(get_async_db),
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
    session = await negotiation_service.negotiation_repo.get_session(session_id)
    if not session:
        raise ApiError(status_code=404, message=f"Session {session_id} not found")

    if session.user_id != current_user.id:
        raise ApiError(
            status_code=403,
            message="You don't have permission to access this session",
        )

    # Get the deal to determine the vehicle price
    deal = await negotiation_service.deal_repo.get(session.deal_id)
    if not deal:
        raise ApiError(status_code=404, message="Associated deal not found")

    # Get the latest messages to find the final negotiated price
    messages = await negotiation_service.negotiation_repo.get_messages(session_id)
    negotiated_price = deal.asking_price

    # Try to find the last suggested price in agent messages (check last 10 messages only)
    for msg in reversed(messages[-10:]):
        if msg.role.value == "agent" and msg.message_metadata:
            if "suggested_price" in msg.message_metadata:
                negotiated_price = msg.message_metadata["suggested_price"]
                break

    # Calculate down payment using shared constant
    down_payment = negotiated_price * NegotiationConfig.DEFAULT_DOWN_PAYMENT_PERCENT
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
    db: AsyncSession = Depends(get_async_db),
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
    session = await service.negotiation_repo.get_session(session_id)
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
    db: AsyncSession = Depends(get_async_db),
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
    session = await service.negotiation_repo.get_session(session_id)
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


@router.websocket("/{session_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """
    WebSocket endpoint for real-time negotiation chat updates

    Provides real-time bidirectional communication for:
    - Instant message delivery
    - Typing indicators
    - Live AI response streaming
    - Connection status updates

    **Path Parameters:**
    - `session_id`: ID of the negotiation session

    **Message Types:**

    Client -> Server:
    - `{"type": "ping"}` - Keep-alive ping
    - `{"type": "subscribe"}` - Subscribe to session updates

    Server -> Client:
    - `{"type": "new_message", "message": {...}}` - New message available
    - `{"type": "typing_indicator", "is_typing": true/false}` - AI typing status
    - `{"type": "error", "error": "..."}` - Error notification
    - `{"type": "pong"}` - Response to ping

    **Authentication**: User-based (JWT) authentication via cookies.
    The authenticated user must own the session or connection is rejected.

    **Connection Lifecycle**:
    1. Client connects to `/api/v1/negotiations/{session_id}/ws`
    2. Server verifies authentication and session ownership
    3. Server accepts connection and adds to connection pool
    4. Client receives real-time updates for the session
    5. On disconnect, connection is removed from pool
    """
    # Get authenticated user from cookie
    access_token = websocket.cookies.get("access_token")
    if not access_token:
        await websocket.close(code=4001, reason="Not authenticated")
        return

    try:
        from app.core.security import decode_token

        payload = decode_token(access_token)
        if not payload or payload.get("type") != "access":
            await websocket.close(code=4001, reason="Invalid token")
            return

        user_id = int(payload.get("sub"))
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            await websocket.close(code=4001, reason="User not found or inactive")
            return
    except (ValueError, TypeError, Exception) as e:
        logger.error(f"WebSocket authentication failed: {str(e)}")
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # Verify session exists before accepting connection
    service = NegotiationService(db)
    session = await service.negotiation_repo.get_session(session_id)

    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    # Verify session belongs to the authenticated user
    if session.user_id != user.id:
        await websocket.close(
            code=4003,
            reason="You don't have permission to access this session",
        )
        return

    # Accept the WebSocket connection
    await connection_manager.connect(websocket, session_id)
    logger.info(f"WebSocket connected for session {session_id} by user {user.id}")

    try:
        while True:
            # Wait for messages from client (mostly for keep-alive)
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif data.get("type") == "subscribe":
                # Client is subscribing to updates (implicit by connection)
                await websocket.send_json({"type": "subscribed", "session_id": session_id})
                logger.debug(f"Client subscribed to session {session_id}")
            else:
                logger.debug(f"Unknown message type: {data.get('type')}")

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {str(e)}")
        connection_manager.disconnect(websocket, session_id)
