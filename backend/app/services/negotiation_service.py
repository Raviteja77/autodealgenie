"""
Negotiation service with LLM integration for multi-round negotiations
"""

import logging
import uuid
from typing import Any, TYPE_CHECKING

from sqlalchemy.orm import Session

from app.llm import generate_text
from app.models.negotiation import MessageRole, NegotiationSession, NegotiationStatus
from app.repositories.deal_repository import DealRepository
from app.repositories.negotiation_repository import NegotiationRepository
from app.services.loan_calculator_service import LoanCalculatorService
from app.utils.error_handler import ApiError

if TYPE_CHECKING:
    from app.services.websocket_manager import ConnectionManager

logger = logging.getLogger(__name__)


class NegotiationService:
    """Service for managing multi-round negotiations with LLM and WebSocket support"""

    MAX_CONVERSATION_HISTORY = 4  # Number of recent messages to include in context
    DEFAULT_DOWN_PAYMENT_PERCENT = 0.10  # 10% down payment
    DEFAULT_CREDIT_SCORE_RANGE = "good"  # Default credit range for calculations
    DEFAULT_TARGET_PRICE_RATIO = 0.9  # Default target price ratio (90% of asking price)
    INITIAL_OFFER_MULTIPLIER = 0.87  # Start 13% below user target price
    
    # Counter offer strategy constants
    EXCELLENT_DISCOUNT_THRESHOLD = 10.0  # 10% off asking price
    GOOD_DISCOUNT_THRESHOLD = 5.0  # 5% off asking price
    HOLD_FIRM_ADJUSTMENT = 1.01  # 1% increase when holding firm
    SMALL_INCREASE_ADJUSTMENT = 1.02  # 2% increase for moderate discount
    AGGRESSIVE_DECREASE_ADJUSTMENT = 0.98  # 2% decrease to pressure dealer

    def __init__(self, db: Session):
        self.db = db
        self.negotiation_repo = NegotiationRepository(db)
        self.deal_repo = DealRepository(db)
        # Lazy import to avoid circular dependency
        self._ws_manager = None

    @property
    def ws_manager(self) -> "ConnectionManager":
        """Lazy load WebSocket manager to avoid circular import"""
        if self._ws_manager is None:
            from app.services.websocket_manager import connection_manager
            self._ws_manager = connection_manager
        return self._ws_manager

    async def _broadcast_message(self, session_id: int, message: Any):
        """
        Broadcast a message via WebSocket to all connected clients
        
        Args:
            session_id: Negotiation session ID
            message: Message object to broadcast
        """
        try:
            message_data = {
                "id": message.id,
                "session_id": message.session_id,
                "role": message.role.value,
                "content": message.content,
                "round_number": message.round_number,
                "metadata": message.message_metadata,
                "created_at": message.created_at.isoformat() if message.created_at else None,
            }
            await self.ws_manager.broadcast_message(session_id, message_data)
        except Exception as e:
            logger.error(f"Failed to broadcast message via WebSocket: {str(e)}")
            # Don't fail the main operation if WebSocket broadcast fails

    def _get_latest_suggested_price(self, session_id: int, default_price: float) -> float:
        """
        Get the latest suggested price from message history
        
        Args:
            session_id: ID of the negotiation session
            default_price: Default price to return if no suggested price found
            
        Returns:
            Latest suggested price or default_price
        """
        messages = self.negotiation_repo.get_messages(session_id)
        for msg in reversed(messages[-10:]):  # Check last 10 messages
            if msg.metadata and "suggested_price" in msg.metadata:
                return msg.metadata["suggested_price"]
        return default_price

    async def create_negotiation(
        self,
        user_id: int,
        deal_id: int,
        user_target_price: float,
        strategy: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new negotiation session and seed the first round

        Args:
            user_id: ID of the user initiating negotiation
            deal_id: ID of the deal being negotiated
            user_target_price: User's target price
            strategy: Optional negotiation strategy

        Returns:
            Dictionary with session details and initial response

        Raises:
            ApiError: If deal not found or other errors occur
        """
        request_id = str(uuid.uuid4())
        logger.info(
            f"[{request_id}] Creating negotiation session for user {user_id}, deal {deal_id}"
        )

        # Validate deal exists
        deal = self.deal_repo.get(deal_id)
        if not deal:
            logger.error(f"[{request_id}] Deal {deal_id} not found")
            raise ApiError(status_code=404, message=f"Deal with id {deal_id} not found")

        # Create session
        session = self.negotiation_repo.create_session(user_id=user_id, deal_id=deal_id)
        logger.info(f"[{request_id}] Created session {session.id}")

        # Add initial user message
        user_message = (
            f"I'm interested in the {deal.vehicle_year} {deal.vehicle_make} "
            f"{deal.vehicle_model}. The asking price is ${deal.asking_price:,.2f}, "
            f"but my target price is ${user_target_price:,.2f}."
        )
        if strategy:
            user_message += f" My negotiation approach is {strategy}."

        user_msg = self.negotiation_repo.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content=user_message,
            round_number=1,
            metadata={"target_price": user_target_price, "strategy": strategy},
        )
        
        # Broadcast user message via WebSocket
        await self._broadcast_message(session.id, user_msg)

        # Generate agent's initial response using LLM
        try:
            # Show typing indicator
            await self.ws_manager.broadcast_typing_indicator(session.id, True)
            
            agent_response = await self._generate_agent_response(
                session=session,
                deal=deal,
                user_target_price=user_target_price,
                strategy=strategy,
                request_id=request_id,
            )

            # Hide typing indicator
            await self.ws_manager.broadcast_typing_indicator(session.id, False)
            
            agent_msg = self.negotiation_repo.add_message(
                session_id=session.id,
                role=MessageRole.AGENT,
                content=agent_response["content"],
                round_number=1,
                metadata=agent_response["metadata"],
            )
            
            # Broadcast agent message via WebSocket
            await self._broadcast_message(session.id, agent_msg)

            logger.info(f"[{request_id}] Session {session.id} initialized successfully")

            return {
                "session_id": session.id,
                "status": session.status.value,
                "current_round": session.current_round,
                "agent_message": agent_response["content"],
                "metadata": agent_response["metadata"],
            }

        except Exception as e:
            logger.error(f"[{request_id}] Error generating agent response: {str(e)}")
            raise ApiError(
                status_code=500,
                message="Failed to generate negotiation response",
                details={"error": str(e)},
            ) from e

    async def process_next_round(
        self,
        session_id: int,
        user_action: str,
        counter_offer: float | None = None,
    ) -> dict[str, Any]:
        """
        Process the next round of negotiation

        Args:
            session_id: ID of the negotiation session
            user_action: User's action (confirm, reject, counter)
            counter_offer: Optional counter offer price

        Returns:
            Dictionary with updated session status and agent response

        Raises:
            ApiError: If session not found, inactive, or max rounds exceeded
        """
        request_id = str(uuid.uuid4())
        logger.info(f"[{request_id}] Processing next round for session {session_id}")

        # Get session
        session = self.negotiation_repo.get_session(session_id)
        if not session:
            logger.error(f"[{request_id}] Session {session_id} not found")
            raise ApiError(status_code=404, message=f"Session {session_id} not found")

        # Check session is active
        if session.status != NegotiationStatus.ACTIVE:
            logger.error(f"[{request_id}] Session {session_id} is not active")
            raise ApiError(
                status_code=400,
                message="Session is not active",
                details={"status": session.status.value},
            )

        # Check max rounds
        if session.current_round >= session.max_rounds:
            logger.warning(f"[{request_id}] Session {session_id} reached max rounds")
            self.negotiation_repo.update_session_status(session_id, NegotiationStatus.COMPLETED)
            raise ApiError(
                status_code=400,
                message="Maximum negotiation rounds reached",
                details={"max_rounds": session.max_rounds},
            )

        # Get deal
        deal = self.deal_repo.get(session.deal_id)
        if not deal:
            logger.error(f"[{request_id}] Deal {session.deal_id} not found")
            raise ApiError(status_code=404, message="Associated deal not found")

        # Handle user action
        if user_action == "confirm":
            # User accepts the deal
            self.negotiation_repo.update_session_status(session_id, NegotiationStatus.COMPLETED)

            message_content = "Thank you! I accept the current offer."
            self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=message_content,
                round_number=session.current_round,
                metadata={"action": "confirm"},
            )

            agent_content = (
                "Excellent! The deal is confirmed. " "We'll proceed with finalizing the paperwork."
            )
            self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.AGENT,
                content=agent_content,
                round_number=session.current_round,
                metadata={"action": "deal_confirmed"},
            )

            logger.info(f"[{request_id}] Session {session_id} completed (user confirmed)")
            return {
                "session_id": session_id,
                "status": NegotiationStatus.COMPLETED.value,
                "current_round": session.current_round,
                "agent_message": agent_content,
                "metadata": {"action": "deal_confirmed"},
            }

        elif user_action == "reject":
            # User rejects and ends negotiation
            self.negotiation_repo.update_session_status(session_id, NegotiationStatus.CANCELLED)

            message_content = "I'm not interested in continuing this negotiation."
            self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=message_content,
                round_number=session.current_round,
                metadata={"action": "reject"},
            )

            agent_content = (
                "I understand. Thank you for your time. "
                "Feel free to reach out if you change your mind."
            )
            self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.AGENT,
                content=agent_content,
                round_number=session.current_round,
                metadata={"action": "negotiation_cancelled"},
            )

            logger.info(f"[{request_id}] Session {session_id} cancelled (user rejected)")
            return {
                "session_id": session_id,
                "status": NegotiationStatus.CANCELLED.value,
                "current_round": session.current_round,
                "agent_message": agent_content,
                "metadata": {"action": "negotiation_cancelled"},
            }

        elif user_action == "counter":
            # User makes a counter offer
            if counter_offer is None or counter_offer <= 0:
                raise ApiError(
                    status_code=400,
                    message="Counter offer is required for counter action",
                )

            # Increment round
            session = self.negotiation_repo.increment_round(session_id)

            # Add user counter message
            message_content = f"I'd like to counter with an offer of ${counter_offer:,.2f}."
            user_msg = self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=message_content,
                round_number=session.current_round,
                metadata={"action": "counter", "counter_offer": counter_offer},
            )
            
            # Broadcast user message via WebSocket
            await self._broadcast_message(session_id, user_msg)

            # Generate agent's counter response using LLM
            try:
                # Show typing indicator
                await self.ws_manager.broadcast_typing_indicator(session_id, True)
                
                agent_response = await self._generate_counter_response(
                    session=session,
                    deal=deal,
                    counter_offer=counter_offer,
                    request_id=request_id,
                )

                # Hide typing indicator
                await self.ws_manager.broadcast_typing_indicator(session_id, False)
                
                agent_msg = self.negotiation_repo.add_message(
                    session_id=session_id,
                    role=MessageRole.AGENT,
                    content=agent_response["content"],
                    round_number=session.current_round,
                    metadata=agent_response["metadata"],
                )
                
                # Broadcast agent message via WebSocket
                await self._broadcast_message(session_id, agent_msg)

                logger.info(
                    f"[{request_id}] Session {session_id} advanced to round {session.current_round}"
                )

                return {
                    "session_id": session_id,
                    "status": session.status.value,
                    "current_round": session.current_round,
                    "agent_message": agent_response["content"],
                    "metadata": agent_response["metadata"],
                }

            except Exception as e:
                logger.error(f"[{request_id}] Error generating counter response: {str(e)}")
                raise ApiError(
                    status_code=500,
                    message="Failed to generate negotiation response",
                    details={"error": str(e)},
                ) from e

        else:
            raise ApiError(
                status_code=400,
                message="Invalid user action",
                details={"valid_actions": ["confirm", "reject", "counter"]},
            )

    async def _generate_agent_response(
        self,
        session: NegotiationSession,
        deal: Any,
        user_target_price: float,
        strategy: str | None,
        request_id: str,
    ) -> dict[str, Any]:
        """Generate agent's initial response using LLM"""
        logger.info(f"[{request_id}] Generating agent response for session {session.id}")

        try:
            # Use centralized LLM client
            response_content = generate_text(
                prompt_id="negotiation_initial",
                variables={
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "mileage": f"{deal.vehicle_mileage:,}",
                    "asking_price": f"{deal.asking_price:,.2f}",
                    "target_price": f"{user_target_price:,.2f}",
                    "strategy": strategy or "Not specified",
                },
                temperature=0.7,
            )

            # Generate suggested counter offer - start BELOW user's target to leave negotiating room
            # User-centric approach: suggest 10-15% below target price for initial offer
            suggested_price = user_target_price * self.INITIAL_OFFER_MULTIPLIER

            # Calculate financing options for the suggested price
            financing_options = self._calculate_financing_options(suggested_price)

            # Calculate cash savings (cash price vs total financed cost)
            cash_savings = None
            if financing_options:
                # Use 60-month term as baseline for comparison
                baseline_financing = next(
                    (opt for opt in financing_options if opt["loan_term_months"] == 60),
                    financing_options[0] if financing_options else None,
                )
                if baseline_financing:
                    cash_savings = baseline_financing["total_cost"] - suggested_price

            return {
                "content": response_content,
                "metadata": {
                    "suggested_price": round(suggested_price, 2),
                    "asking_price": deal.asking_price,
                    "user_target_price": user_target_price,
                    "financing_options": financing_options,
                    "cash_savings": round(cash_savings, 2) if cash_savings else None,
                    "llm_used": True,
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] LLM call failed: {str(e)}")
            # Fallback response if LLM fails
            fallback_content = (
                f"Thank you for your interest in the {deal.vehicle_year} "
                f"{deal.vehicle_make} {deal.vehicle_model}. "
                f"Your target of ${user_target_price:,.2f} is realistic given the asking price of ${deal.asking_price:,.2f}. "
                f"I recommend starting with a lower initial offer to give you negotiating room. "
                f"This is a smart strategy that maximizes your chances of getting the best deal."
            )

            # Start BELOW user's target price
            suggested_price = user_target_price * self.INITIAL_OFFER_MULTIPLIER

            # Calculate financing options even for fallback
            financing_options = self._calculate_financing_options(suggested_price)

            # Calculate cash savings
            cash_savings = None
            if financing_options:
                baseline_financing = next(
                    (opt for opt in financing_options if opt["loan_term_months"] == 60),
                    financing_options[0] if financing_options else None,
                )
                if baseline_financing:
                    cash_savings = baseline_financing["total_cost"] - suggested_price

            return {
                "content": fallback_content,
                "metadata": {
                    "suggested_price": round(suggested_price, 2),
                    "asking_price": deal.asking_price,
                    "user_target_price": user_target_price,
                    "financing_options": financing_options,
                    "cash_savings": round(cash_savings, 2) if cash_savings else None,
                    "llm_used": False,
                    "fallback": True,
                },
            }

    def _calculate_financing_options(
        self, vehicle_price: float, credit_score_range: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Calculate multiple financing options for different loan terms

        Args:
            vehicle_price: Current negotiated vehicle price
            credit_score_range: Credit score range (defaults to 'good')

        Returns:
            List of financing option dictionaries
        """
        if credit_score_range is None:
            credit_score_range = self.DEFAULT_CREDIT_SCORE_RANGE

        # Calculate down payment (10% of price)
        down_payment = vehicle_price * self.DEFAULT_DOWN_PAYMENT_PERCENT

        # Common loan terms to calculate (in months)
        loan_terms = [36, 48, 60, 72]
        financing_options = []

        for term_months in loan_terms:
            try:
                # Calculate loan details using LoanCalculatorService
                loan_result = LoanCalculatorService.calculate_loan(
                    loan_amount=vehicle_price,
                    down_payment=down_payment,
                    loan_term_months=term_months,
                    credit_score_range=credit_score_range,
                    include_amortization=False,
                )

                financing_options.append(
                    {
                        "loan_amount": loan_result.principal,
                        "down_payment": loan_result.down_payment,
                        "monthly_payment_estimate": loan_result.monthly_payment,
                        "loan_term_months": loan_result.loan_term_months,
                        "estimated_apr": loan_result.apr,
                        "total_cost": loan_result.total_amount + loan_result.down_payment,
                        "total_interest": loan_result.total_interest,
                    }
                )
            except ValueError as e:
                logger.warning(
                    f"Failed to calculate financing for {term_months} month term: {str(e)}"
                )
                continue
            except Exception as e:
                logger.exception(
                    f"Unexpected error calculating financing for {term_months} month term: {str(e)}"
                )
                # Continue to try other terms rather than failing completely
                continue

        return financing_options

    async def _generate_counter_response(
        self,
        session: NegotiationSession,
        deal: Any,
        counter_offer: float,
        request_id: str,
    ) -> dict[str, Any]:
        """Generate agent's counter response using LLM"""
        logger.info(f"[{request_id}] Generating counter response for session {session.id}")

        # Get conversation history
        messages = self.negotiation_repo.get_messages(session.id)
        offer_history = []
        for msg in messages[-self.MAX_CONVERSATION_HISTORY :]:  # Last N messages
            if msg.metadata and "counter_offer" in msg.metadata:
                offer_history.append(f"${msg.metadata['counter_offer']:,.2f}")
            elif msg.metadata and "suggested_price" in msg.metadata:
                offer_history.append(f"${msg.metadata['suggested_price']:,.2f}")

        try:
            # Use centralized LLM client
            response_content = generate_text(
                prompt_id="negotiation_counter",
                variables={
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "mileage": f"{deal.vehicle_mileage:,}",
                    "asking_price": f"{deal.asking_price:,.2f}",
                    "counter_offer": f"{counter_offer:,.2f}",
                    "round_number": session.current_round,
                    "offer_history": ", ".join(offer_history) if offer_history else "None",
                },
                temperature=0.7,
            )

            # Generate new suggested price - favor the USER, not dealer
            # Instead of converging to asking price, suggest user holds firm or goes slightly lower
            # This encourages aggressive negotiation that benefits the user
            
            # Calculate how much room there is between counter offer and asking price
            price_gap = deal.asking_price - counter_offer
            
            # If user is already getting a good deal (>10% off asking), validate and hold firm
            discount_percent = (price_gap / deal.asking_price) * 100
            
            if discount_percent >= self.EXCELLENT_DISCOUNT_THRESHOLD:
                # User is already getting 10%+ off - suggest holding firm or minimal increase
                new_suggested_price = counter_offer * self.HOLD_FIRM_ADJUSTMENT
            elif discount_percent >= self.GOOD_DISCOUNT_THRESHOLD:
                # User getting 5-10% off - suggest small increase
                new_suggested_price = counter_offer * self.SMALL_INCREASE_ADJUSTMENT
            else:
                # User not getting good deal yet - suggest aggressive stance
                # Go slightly lower to pressure dealer
                new_suggested_price = counter_offer * self.AGGRESSIVE_DECREASE_ADJUSTMENT

            # Calculate financing options for the new suggested price
            financing_options = self._calculate_financing_options(new_suggested_price)

            # Calculate cash savings (cash price vs total financed cost)
            cash_savings = None
            if financing_options:
                # Use 60-month term as baseline for comparison
                baseline_financing = next(
                    (opt for opt in financing_options if opt["loan_term_months"] == 60),
                    financing_options[0] if financing_options else None,
                )
                if baseline_financing:
                    cash_savings = baseline_financing["total_cost"] - new_suggested_price

            return {
                "content": response_content,
                "metadata": {
                    "suggested_price": round(new_suggested_price, 2),
                    "user_counter_offer": counter_offer,
                    "asking_price": deal.asking_price,
                    "financing_options": financing_options,
                    "cash_savings": round(cash_savings, 2) if cash_savings else None,
                    "llm_used": True,
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] LLM call failed: {str(e)}")
            # Fallback response - user-centric approach
            price_gap = deal.asking_price - counter_offer
            discount_percent = (price_gap / deal.asking_price) * 100
            
            if discount_percent >= self.EXCELLENT_DISCOUNT_THRESHOLD:
                new_suggested_price = counter_offer * self.HOLD_FIRM_ADJUSTMENT
                fallback_content = (
                    f"Your offer of ${counter_offer:,.2f} is excellent - you're getting over 10% off! "
                    f"I'd suggest holding firm at this price or going only slightly higher to ${new_suggested_price:,.2f}. "
                    f"You're in a strong negotiating position."
                )
            elif discount_percent >= self.GOOD_DISCOUNT_THRESHOLD:
                new_suggested_price = counter_offer * self.SMALL_INCREASE_ADJUSTMENT
                fallback_content = (
                    f"Your offer of ${counter_offer:,.2f} is solid. "
                    f"You could go up to ${new_suggested_price:,.2f}, but I'd encourage you to push for "
                    f"a better deal. Consider holding your ground or only increasing minimally."
                )
            else:
                new_suggested_price = counter_offer * self.AGGRESSIVE_DECREASE_ADJUSTMENT
                fallback_content = (
                    f"Your offer of ${counter_offer:,.2f} is reasonable, but you might be able to do better. "
                    f"Consider actually going LOWER to ${new_suggested_price:,.2f} to test the dealer's flexibility. "
                    f"Remember, you have leverage - you can always walk away."
                )

            # Calculate financing options even for fallback
            financing_options = self._calculate_financing_options(new_suggested_price)

            # Calculate cash savings
            cash_savings = None
            if financing_options:
                baseline_financing = next(
                    (opt for opt in financing_options if opt["loan_term_months"] == 60),
                    financing_options[0] if financing_options else None,
                )
                if baseline_financing:
                    cash_savings = baseline_financing["total_cost"] - new_suggested_price

            return {
                "content": fallback_content,
                "metadata": {
                    "suggested_price": round(new_suggested_price, 2),
                    "user_counter_offer": counter_offer,
                    "asking_price": deal.asking_price,
                    "financing_options": financing_options,
                    "cash_savings": round(cash_savings, 2) if cash_savings else None,
                    "llm_used": False,
                    "fallback": True,
                },
            }

    def get_session_with_messages(self, session_id: int) -> dict[str, Any] | None:
        """
        Get a negotiation session with all its messages

        Args:
            session_id: ID of the negotiation session

        Returns:
            Dictionary with session details and messages, or None if not found
        """
        session = self.negotiation_repo.get_session(session_id)
        if not session:
            return None

        messages = self.negotiation_repo.get_messages(session_id)

        return {
            "id": session.id,
            "user_id": session.user_id,
            "deal_id": session.deal_id,
            "status": session.status.value,
            "current_round": session.current_round,
            "max_rounds": session.max_rounds,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "messages": [
                {
                    "id": msg.id,
                    "session_id": msg.session_id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "round_number": msg.round_number,
                    "metadata": msg.message_metadata,
                    "created_at": msg.created_at,
                }
                for msg in messages
            ],
        }

    async def send_chat_message(
        self,
        session_id: int,
        user_message: str,
        message_type: str = "general",
    ) -> dict[str, Any]:
        """
        Send a free-form chat message and get AI response

        Args:
            session_id: ID of the negotiation session
            user_message: User's message content
            message_type: Type of message (general, question, etc.)

        Returns:
            Dictionary with user message and agent response

        Raises:
            ApiError: If session not found or not active
        """
        request_id = str(uuid.uuid4())
        logger.info(f"[{request_id}] Processing chat message for session {session_id}")

        # Get session
        session = self.negotiation_repo.get_session(session_id)
        if not session:
            logger.error(f"[{request_id}] Session {session_id} not found")
            raise ApiError(status_code=404, message=f"Session {session_id} not found")

        # Allow chat even if session is completed/cancelled for post-negotiation questions
        # Get deal
        deal = self.deal_repo.get(session.deal_id)
        if not deal:
            logger.error(f"[{request_id}] Deal {session.deal_id} not found")
            raise ApiError(status_code=404, message="Associated deal not found")

        # Add user message
        user_msg = self.negotiation_repo.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=user_message,
            round_number=session.current_round,
            metadata={"message_type": message_type, "chat_message": True},
        )
        
        # Broadcast user message via WebSocket
        await self._broadcast_message(session_id, user_msg)

        # Generate agent response
        try:
            # Show typing indicator
            await self.ws_manager.broadcast_typing_indicator(session_id, True)
            
            agent_response = await self._generate_chat_response(
                session=session,
                deal=deal,
                user_message=user_message,
                request_id=request_id,
            )

            # Hide typing indicator
            await self.ws_manager.broadcast_typing_indicator(session_id, False)
            
            agent_msg = self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.AGENT,
                content=agent_response["content"],
                round_number=session.current_round,
                metadata={**agent_response["metadata"], "chat_message": True},
            )
            
            # Broadcast agent message via WebSocket
            await self._broadcast_message(session_id, agent_msg)

            logger.info(f"[{request_id}] Chat message processed successfully")

            return {
                "session_id": session_id,
                "status": session.status.value,
                "user_message": {
                    "id": user_msg.id,
                    "session_id": user_msg.session_id,
                    "role": user_msg.role.value,
                    "content": user_msg.content,
                    "round_number": user_msg.round_number,
                    "metadata": user_msg.message_metadata,
                    "created_at": user_msg.created_at,
                },
                "agent_message": {
                    "id": agent_msg.id,
                    "session_id": agent_msg.session_id,
                    "role": agent_msg.role.value,
                    "content": agent_msg.content,
                    "round_number": agent_msg.round_number,
                    "metadata": agent_msg.message_metadata,
                    "created_at": agent_msg.created_at,
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] Error generating chat response: {str(e)}")
            raise ApiError(
                status_code=500,
                message="Failed to generate chat response",
                details={"error": str(e)},
            ) from e

    async def _generate_chat_response(
        self,
        session: NegotiationSession,
        deal: Any,
        user_message: str,
        request_id: str,
    ) -> dict[str, Any]:
        """Generate AI response to free-form chat message"""
        logger.info(f"[{request_id}] Generating chat response for session {session.id}")

        # Get recent conversation history
        messages = self.negotiation_repo.get_messages(session.id)
        recent_messages = messages[-6:]  # Last 6 messages for context

        conversation_history = []
        for msg in recent_messages:
            role_label = "User" if msg.role == MessageRole.USER else "AI"
            conversation_history.append(f"{role_label}: {msg.content}")

        # Get latest suggested price using helper method
        suggested_price = self._get_latest_suggested_price(session.id, deal.asking_price)

        try:
            # Use centralized LLM client
            response_content = generate_text(
                prompt_id="negotiation_chat",
                variables={
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "asking_price": f"{deal.asking_price:,.2f}",
                    "current_round": session.current_round,
                    "suggested_price": f"{suggested_price:,.2f}",
                    "status": session.status.value,
                    "conversation_history": "\n".join(conversation_history[-4:]),
                    "user_message": user_message,
                },
                temperature=0.8,
            )

            return {
                "content": response_content,
                "metadata": {
                    "llm_used": True,
                    "message_type": "chat_response",
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] LLM call failed for chat: {str(e)}")
            # Fallback response
            fallback_content = (
                "Thank you for your message. I'm here to help you with your negotiation. "
                "LLM service is currently unavailable, but I recommend staying focused on your target price."
            )

            return {
                "content": fallback_content,
                "metadata": {
                    "llm_used": False,
                    "fallback": True,
                    "message_type": "chat_response",
                },
            }

    async def analyze_dealer_info(
        self,
        session_id: int,
        info_type: str,
        content: str,
        price_mentioned: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze dealer-provided information and provide recommendations

        Args:
            session_id: ID of the negotiation session
            info_type: Type of dealer info
            content: Dealer information content
            price_mentioned: Price mentioned in dealer info
            metadata: Additional structured data

        Returns:
            Dictionary with analysis and recommendations

        Raises:
            ApiError: If session not found or inactive
        """
        request_id = str(uuid.uuid4())
        logger.info(f"[{request_id}] Analyzing dealer info for session {session_id}")

        # Get session
        session = self.negotiation_repo.get_session(session_id)
        if not session:
            logger.error(f"[{request_id}] Session {session_id} not found")
            raise ApiError(status_code=404, message=f"Session {session_id} not found")

        # Check session is active
        if session.status != NegotiationStatus.ACTIVE:
            logger.error(f"[{request_id}] Session {session_id} is not active")
            raise ApiError(
                status_code=400,
                message="Session is not active",
                details={"status": session.status.value},
            )

        # Get deal
        deal = self.deal_repo.get(session.deal_id)
        if not deal:
            logger.error(f"[{request_id}] Deal {session.deal_id} not found")
            raise ApiError(status_code=404, message="Associated deal not found")

        # Add user message with dealer info
        user_msg_content = f"[Dealer Information - {info_type}]\n{content}"
        if price_mentioned:
            user_msg_content += f"\n\nPrice mentioned: ${price_mentioned:,.2f}"

        user_msg = self.negotiation_repo.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=user_msg_content,
            round_number=session.current_round,
            metadata={
                "message_type": "dealer_info",
                "info_type": info_type,
                "price_mentioned": price_mentioned,
                "additional_metadata": metadata,
            },
        )

        # Generate analysis
        try:
            agent_response = await self._generate_dealer_info_analysis(
                session=session,
                deal=deal,
                info_type=info_type,
                content=content,
                price_mentioned=price_mentioned,
                request_id=request_id,
            )

            agent_msg = self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.AGENT,
                content=agent_response["content"],
                round_number=session.current_round,
                metadata=agent_response["metadata"],
            )

            logger.info(f"[{request_id}] Dealer info analyzed successfully")

            return {
                "session_id": session_id,
                "status": session.status.value,
                "analysis": agent_response["content"],
                "recommended_action": agent_response["metadata"].get("recommended_action"),
                "user_message": {
                    "id": user_msg.id,
                    "session_id": user_msg.session_id,
                    "role": user_msg.role.value,
                    "content": user_msg.content,
                    "round_number": user_msg.round_number,
                    "metadata": user_msg.message_metadata,
                    "created_at": user_msg.created_at,
                },
                "agent_message": {
                    "id": agent_msg.id,
                    "session_id": agent_msg.session_id,
                    "role": agent_msg.role.value,
                    "content": agent_msg.content,
                    "round_number": agent_msg.round_number,
                    "metadata": agent_msg.message_metadata,
                    "created_at": agent_msg.created_at,
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] Error analyzing dealer info: {str(e)}")
            raise ApiError(
                status_code=500,
                message="Failed to analyze dealer information",
                details={"error": str(e)},
            ) from e

    async def _generate_dealer_info_analysis(
        self,
        session: NegotiationSession,
        deal: Any,
        info_type: str,
        content: str,
        price_mentioned: float | None,
        request_id: str,
    ) -> dict[str, Any]:
        """Generate AI analysis of dealer-provided information"""
        logger.info(f"[{request_id}] Generating dealer info analysis for session {session.id}")

        # Get latest suggested price using helper method
        suggested_price = self._get_latest_suggested_price(session.id, deal.asking_price)
        
        # Get user target price from messages or use default
        messages = self.negotiation_repo.get_messages(session.id)
        user_target = deal.asking_price * self.DEFAULT_TARGET_PRICE_RATIO
        
        for msg in reversed(messages[-10:]):
            if msg.metadata and "target_price" in msg.metadata:
                user_target = msg.metadata["target_price"]
                break

        try:
            # Use centralized LLM client
            response_content = generate_text(
                prompt_id="dealer_info_analysis",
                variables={
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "asking_price": f"{deal.asking_price:,.2f}",
                    "current_round": session.current_round,
                    "suggested_price": f"{suggested_price:,.2f}",
                    "user_target": f"{user_target:,.2f}",
                    "info_type": info_type,
                    "dealer_content": content,
                    "price_mentioned": f"${price_mentioned:,.2f}" if price_mentioned else "None",
                },
                temperature=0.7,
            )

            # Determine recommended action based on dealer info
            recommended_action = None
            if price_mentioned:
                if price_mentioned <= user_target:
                    recommended_action = "accept"
                elif price_mentioned <= suggested_price:
                    recommended_action = "consider"
                else:
                    recommended_action = "counter"

            return {
                "content": response_content,
                "metadata": {
                    "llm_used": True,
                    "message_type": "dealer_info_analysis",
                    "info_type": info_type,
                    "price_mentioned": price_mentioned,
                    "recommended_action": recommended_action,
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] LLM call failed for dealer info analysis: {str(e)}")
            # Fallback response
            fallback_content = (
                f"I've received the dealer information ({info_type}). "
                f"Based on the current negotiation context, "
            )

            if price_mentioned:
                if price_mentioned <= user_target:
                    fallback_content += (
                        f"the dealer's price of ${price_mentioned:,.2f} is at or below your "
                        f"target. This appears to be a good deal. Consider accepting it."
                    )
                    recommended_action = "accept"
                elif price_mentioned <= suggested_price:
                    fallback_content += (
                        f"the dealer's price of ${price_mentioned:,.2f} is reasonable but "
                        f"you might be able to negotiate further. Consider countering with "
                        f"a price closer to your target."
                    )
                    recommended_action = "consider"
                else:
                    fallback_content += (
                        f"the dealer's price of ${price_mentioned:,.2f} is still above our "
                        f"recommended range. I suggest making another counter offer."
                    )
                    recommended_action = "counter"
            else:
                fallback_content += (
                    "please review this information carefully. Let me know if you'd like to "
                    "discuss how to proceed with the negotiation."
                )

            return {
                "content": fallback_content,
                "metadata": {
                    "llm_used": False,
                    "fallback": True,
                    "message_type": "dealer_info_analysis",
                    "info_type": info_type,
                    "price_mentioned": price_mentioned,
                    "recommended_action": recommended_action,
                },
            }
