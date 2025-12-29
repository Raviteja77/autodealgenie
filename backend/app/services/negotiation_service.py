"""
Negotiation service with LLM integration for multi-round negotiations
"""

import logging
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.llm import generate_text
from app.models.negotiation import MessageRole, NegotiationSession, NegotiationStatus
from app.repositories.ai_response_repository import AIResponseRepository
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

    def __init__(self, db: AsyncSession):
        self.db = db
        self.negotiation_repo = NegotiationRepository(db)
        self.deal_repo = DealRepository(db)
        self.ai_response_repo = AIResponseRepository(db)
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

    async def _get_latest_suggested_price(self, session_id: int, default_price: float) -> float:
        """
        Get the latest suggested price from message history

        Args:
            session_id: ID of the negotiation session
            default_price: Default price to return if no suggested price found

        Returns:
            Latest suggested price or default_price
        """
        messages =            await self.negotiation_repo.get_messages(session_id)
        for msg in reversed(messages[-10:]):  # Check last 10 messages
            if msg.message_metadata and "suggested_price" in msg.message_metadata:
                return msg.message_metadata["suggested_price"]
        return default_price

    async def create_negotiation(
        self,
        user_id: int,
        deal_id: int,
        user_target_price: float,
        strategy: str | None = None,
        evaluation_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new negotiation session and seed the first round

        Args:
            user_id: ID of the user initiating negotiation
            deal_id: ID of the deal being negotiated
            user_target_price: User's target price
            strategy: Optional negotiation strategy
            evaluation_data: Optional evaluation results from deal evaluation (recommended)

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
        deal =            await self.deal_repo.get(deal_id)
        if not deal:
            logger.error(f"[{request_id}] Deal {deal_id} not found")
            raise ApiError(status_code=404, message=f"Deal with id {deal_id} not found")

        # Log if evaluation data is provided
        if evaluation_data:
            logger.info(
                f"[{request_id}] Negotiation using evaluation data: "
                f"Fair value: ${evaluation_data.get('fair_value', 'N/A')}, "
                f"Score: {evaluation_data.get('score', 'N/A')}"
            )

        # Create session with evaluation data in metadata
        session =            await self.negotiation_repo.create_session(user_id=user_id, deal_id=deal_id)
        logger.info(f"[{request_id}] Created session {session.id}")

        # Add initial user message
        user_message = (
            f"I'm interested in the {deal.vehicle_year} {deal.vehicle_make} "
            f"{deal.vehicle_model}. The asking price is ${deal.asking_price:,.2f}, "
            f"but my target price is ${user_target_price:,.2f}."
        )
        if strategy:
            user_message += f" My negotiation approach is {strategy}."

        # Include evaluation context in metadata
        message_metadata = {
            "target_price": user_target_price,
            "strategy": strategy,
        }
        if evaluation_data:
            message_metadata["evaluation_data"] = {
                "fair_value": evaluation_data.get("fair_value"),
                "score": evaluation_data.get("score"),
                "has_market_data": bool(evaluation_data.get("market_data")),
            }

        user_msg =            await self.negotiation_repo.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content=user_message,
            round_number=1,
            metadata=message_metadata,
        )

        # Broadcast user message via WebSocket
            await self._broadcast_message(session.id, user_msg)

        # Generate agent's initial response using LLM with evaluation data
        try:
            # Show typing indicator
            await self.ws_manager.broadcast_typing_indicator(session.id, True)

            agent_response =            await self._generate_agent_response(
                session=session,
                deal=deal,
                user_target_price=user_target_price,
                strategy=strategy,
                request_id=request_id,
                evaluation_data=evaluation_data,
            )

            # Hide typing indicator
            await self.ws_manager.broadcast_typing_indicator(session.id, False)

            agent_msg =            await self.negotiation_repo.add_message(
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
        session =            await self.negotiation_repo.get_session(session_id)
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
            await self.negotiation_repo.update_session_status(session_id, NegotiationStatus.COMPLETED)
            raise ApiError(
                status_code=400,
                message="Maximum negotiation rounds reached",
                details={"max_rounds": session.max_rounds},
            )

        # Get deal
        deal =            await self.deal_repo.get(session.deal_id)
        if not deal:
            logger.error(f"[{request_id}] Deal {session.deal_id} not found")
            raise ApiError(status_code=404, message="Associated deal not found")

        # Handle user action
        if user_action == "confirm":
            # User accepts the deal - update negotiation status
            await self.negotiation_repo.update_session_status(session_id, NegotiationStatus.COMPLETED)

            # Get the latest negotiated price to update the deal
            latest_price = self._get_latest_suggested_price(session_id, deal.asking_price)

            # Update the deal with the final negotiated price and status
            from app.schemas.schemas import DealUpdate

            deal_update = DealUpdate(
                offer_price=latest_price,
                status="completed",
                notes=f"{deal.notes or ''}\nNegotiation completed. Final agreed price: ${latest_price:,.2f}".strip(),
            )
            await self.deal_repo.update(session.deal_id, deal_update)
            logger.info(
                f"[{request_id}] Deal {session.deal_id} updated - "
                f"Status: completed, Offer Price: ${latest_price:,.2f}"
            )

            message_content = "Thank you! I accept the current offer."
            await self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=message_content,
                round_number=session.current_round,
                metadata={"action": "confirm"},
            )

            agent_content = (
                "Excellent! The deal is confirmed. " "We'll proceed with finalizing the paperwork."
            )
            await self.negotiation_repo.add_message(
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
            await self.negotiation_repo.update_session_status(session_id, NegotiationStatus.CANCELLED)

            message_content = "I'm not interested in continuing this negotiation."
            await self.negotiation_repo.add_message(
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
            await self.negotiation_repo.add_message(
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
            session =            await self.negotiation_repo.increment_round(session_id)

            # Add user counter message
            message_content = f"I'd like to counter with an offer of ${counter_offer:,.2f}."
            user_msg =            await self.negotiation_repo.add_message(
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

                agent_response =            await self._generate_counter_response(
                    session=session,
                    deal=deal,
                    counter_offer=counter_offer,
                    request_id=request_id,
                )

                # Hide typing indicator
            await self.ws_manager.broadcast_typing_indicator(session_id, False)

                agent_msg =            await self.negotiation_repo.add_message(
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

    async def _calculate_ai_metrics(
        self,
        session_id: int,
        deal: Any,
        current_price: float,
        user_target: float,
        messages: list[Any] | None = None,
    ) -> dict[str, Any]:
        """
        Calculate enhanced AI metrics for negotiation intelligence

        Args:
            session_id: Session ID for message history
            deal: Deal object with asking price
            current_price: Current suggested/negotiated price
            user_target: User's target price
            messages: Optional pre-fetched messages to avoid redundant queries

        Returns:
            Dictionary with AI metrics including confidence, recommendations, etc.
        """
        # Use provided messages or fetch if not provided
        if messages is None:
            messages = await self.negotiation_repo.get_messages(session_id)

        # Calculate confidence score based on deal quality
        # Handle edge case where current_price > asking_price (negative discount)
        if deal.asking_price > 0:
            discount_percent = ((deal.asking_price - current_price) / deal.asking_price) * 100
        else:
            discount_percent = 0

        # Confidence based on discount percentage and negotiation progress
        # Handle negative discounts (price increases) with low confidence
        if discount_percent < 0:  # Price increase - very poor deal
            confidence_score = 0.20
        elif discount_percent >= 15:  # Excellent deal (15%+ off)
            confidence_score = 0.95
        elif discount_percent >= 10:  # Very good deal (10-15% off)
            confidence_score = 0.85
        elif discount_percent >= 5:  # Good deal (5-10% off)
            confidence_score = 0.75
        elif discount_percent >= 2:  # Fair deal (2-5% off)
            confidence_score = 0.65
        else:  # Marginal deal (<2% off)
            confidence_score = 0.50

        # Calculate dealer concession rate (total price movement / asking price)
        initial_asking = deal.asking_price
        dealer_concession_rate = (
            (initial_asking - current_price) / initial_asking if initial_asking > 0 else 0
        )

        # Calculate negotiation velocity (average price change per round)
        round_count = max(len({msg.round_number for msg in messages}), 1)
        negotiation_velocity = (initial_asking - current_price) / round_count

        # Determine recommended action
        if discount_percent < 0:  # Price increase
            recommended_action = "reject"
        elif current_price <= user_target:
            recommended_action = "accept"
        elif discount_percent >= 8:  # Getting decent discount
            recommended_action = "consider"
        else:
            recommended_action = "counter"

        # Generate strategy adjustments based on context
        if dealer_concession_rate > 0.10:  # Dealer very flexible
            strategy_adjustments = (
                "Dealer showing strong flexibility. You have significant leverage—push for more!"
            )
        elif dealer_concession_rate > 0.05:  # Moderate flexibility
            strategy_adjustments = (
                "Moderate progress. Consider one more counter to maximize your savings."
            )
        elif round_count > 5:  # Many rounds, little movement
            strategy_adjustments = (
                "Limited movement detected. Consider accepting current offer or walking away."
            )
        elif dealer_concession_rate <= 0.02:  # Early stage with low concession
            strategy_adjustments = (
                "Early in the negotiation, but the dealer has shown limited flexibility so far. "
                "Consider refining your counteroffer rationale and be prepared with a walk-away price "
                "if movement remains minimal."
            )
        else:
            strategy_adjustments = (
                "Early stage. Continue negotiating strategically to secure the best price."
            )

        # Market comparison insight
        if discount_percent < 0:  # Price increase
            market_comparison = f"Warning: Price is {abs(discount_percent):.1f}% above asking. This is unusual and not recommended."
        elif discount_percent >= 10:
            market_comparison = f"Excellent! You're {discount_percent:.1f}% below asking—better than typical market deals."
        elif discount_percent >= 5:
            market_comparison = (
                f"Solid progress at {discount_percent:.1f}% off. Average market discount is 3-7%."
            )
        else:
            market_comparison = (
                f"Currently at {discount_percent:.1f}% off. Most buyers achieve 5-10% discounts."
            )

        return {
            "confidence_score": round(confidence_score, 2),
            "recommended_action": recommended_action,
            "strategy_adjustments": strategy_adjustments,
            "dealer_concession_rate": round(dealer_concession_rate, 3),
            "negotiation_velocity": round(negotiation_velocity, 2),
            "market_comparison": market_comparison,
        }

    async def _generate_agent_response(
        self,
        session: NegotiationSession,
        deal: Any,
        user_target_price: float,
        strategy: str | None,
        request_id: str,
        evaluation_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate agent's initial response using LLM with evaluation context"""
        logger.info(f"[{request_id}] Generating agent response for session {session.id}")

        # Extract evaluation insights if available
        fair_value = evaluation_data.get("fair_value") if evaluation_data else None
        eval_score = evaluation_data.get("score") if evaluation_data else None
        market_data_summary = ""
        if evaluation_data and evaluation_data.get("market_data"):
            market_data_summary = evaluation_data["market_data"].get("summary", "")

        try:
            # Prepare evaluation context for the prompt
            evaluation_context = "No evaluation data available."
            if evaluation_data:
                evaluation_context = (
                    f"Deal Evaluation Results:\n"
                    f"- Fair Market Value: ${fair_value:,.2f} (based on real-time MarketCheck data)\n"
                    f"- Deal Quality Score: {eval_score}/10\n"
                )
                if market_data_summary:
                    evaluation_context += f"- Market Analysis: {market_data_summary}\n"

                insights = evaluation_data.get("insights", [])
                if insights:
                    evaluation_context += f"- Key Insights: {'; '.join(insights[:3])}"

            # Use centralized LLM client with negotiation agent
            response_content = generate_text(
                prompt_id="negotiation_initial",
                variables={
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "mileage": deal.vehicle_mileage,
                    "asking_price": deal.asking_price,
                    "target_price": user_target_price,
                    "strategy": strategy or "Not specified",
                    "evaluation_context": evaluation_context,
                    "fair_value": fair_value or deal.asking_price,
                },
                agent_role="negotiation",
                temperature=0.7,
            )

            # Use fair value from evaluation if available, otherwise use user target
            # This ensures negotiation suggestions are data-driven
            base_price_for_suggestion = fair_value if fair_value else user_target_price

            # Generate suggested counter offer - start BELOW fair value to leave negotiating room
            # If fair value is significantly below asking price, be more aggressive
            if fair_value and fair_value < deal.asking_price * 0.9:
                # Fair value suggests asking price is high - start even lower
                suggested_price = base_price_for_suggestion * 0.95
            else:
                # Standard approach: suggest 10-15% below target
                suggested_price = base_price_for_suggestion * self.INITIAL_OFFER_MULTIPLIER

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

            # Calculate enhanced AI metrics
            # Pass None for messages to fetch them inside the method (first call, no messages yet)
            ai_metrics = await self._calculate_ai_metrics(
                session_id=session.id,
                deal=deal,
                current_price=suggested_price,
                user_target=user_target_price,
                messages=None,  # Will fetch messages inside the method
            )

            # Log AI response for analytics and traceability
            try:
                await self.ai_response_repo.create_response(
                    feature="negotiation",
                    user_id=session.user_id,
                    deal_id=deal.id,
                    prompt_id="negotiation_initial",
                    prompt_variables={
                        "user_target_price": user_target_price,
                        "asking_price": deal.asking_price,
                        "strategy": strategy,
                        "has_evaluation_data": evaluation_data is not None,
                    },
                    response_content=response_content,
                    response_metadata={
                        "suggested_price": suggested_price,
                        "fair_value": fair_value,
                        "evaluation_score": eval_score,
                        "ai_metrics": ai_metrics,
                    },
                    llm_used=True,
                    agent_role="negotiation",
                )
            except Exception as log_error:
                logger.error(f"Failed to log AI response: {log_error}")
                # Don't fail the main operation if logging fails

            return {
                "content": response_content,
                "metadata": {
                    "suggested_price": round(suggested_price, 2),
                    "asking_price": deal.asking_price,
                    "user_target_price": user_target_price,
                    "fair_value": fair_value,
                    "evaluation_score": eval_score,
                    "has_evaluation_data": evaluation_data is not None,
                    "financing_options": financing_options,
                    "cash_savings": round(cash_savings, 2) if cash_savings else None,
                    "llm_used": True,
                    **ai_metrics,  # Include all AI intelligence metrics
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] LLM call failed: {str(e)}")
            # Fallback response if LLM fails
            fair_value_context = ""
            if fair_value:
                fair_value_context = (
                    f" Based on market data, the fair value is around ${fair_value:,.2f}."
                )

            fallback_content = (
                f"Thank you for your interest in the {deal.vehicle_year} "
                f"{deal.vehicle_make} {deal.vehicle_model}. "
                f"Your target of ${user_target_price:,.2f} is realistic given the asking price of ${deal.asking_price:,.2f}."
                f"{fair_value_context} "
                f"I recommend starting with a lower initial offer to give you negotiating room. "
                f"This is a smart strategy that maximizes your chances of getting the best deal."
            )

            # Start BELOW user's target price or fair value
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

            # Calculate enhanced AI metrics even for fallback
            # Pass None for messages to fetch them inside the method (first call, no messages yet)
            ai_metrics = await self._calculate_ai_metrics(
                session_id=session.id,
                deal=deal,
                current_price=suggested_price,
                user_target=user_target_price,
                messages=None,  # Will fetch messages inside the method
            )

            # Log AI fallback response for analytics and traceability
            try:
                await self.ai_response_repo.create_response(
                    feature="negotiation",
                    user_id=session.user_id,
                    deal_id=deal.id,
                    prompt_id="negotiation_initial_fallback",
                    prompt_variables={
                        "user_target_price": user_target_price,
                        "asking_price": deal.asking_price,
                        "strategy": strategy,
                        "has_evaluation_data": evaluation_data is not None,
                    },
                    response_content=fallback_content,
                    response_metadata={
                        "suggested_price": suggested_price,
                        "fair_value": fair_value,
                        "evaluation_score": eval_score,
                        "ai_metrics": ai_metrics,
                        "fallback": True,
                    },
                    llm_used=False,
                    agent_role="negotiation",
                )
            except Exception as log_error:
                logger.error(f"Failed to log AI fallback response: {log_error}")
                # Don't fail the main operation if logging fails

            return {
                "content": fallback_content,
                "metadata": {
                    "suggested_price": round(suggested_price, 2),
                    "asking_price": deal.asking_price,
                    "user_target_price": user_target_price,
                    "fair_value": fair_value,
                    "evaluation_score": eval_score,
                    "has_evaluation_data": evaluation_data is not None,
                    "financing_options": financing_options,
                    "cash_savings": round(cash_savings, 2) if cash_savings else None,
                    "llm_used": False,
                    "fallback": True,
                    **ai_metrics,  # Include all AI intelligence metrics
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
        messages =            await self.negotiation_repo.get_messages(session.id)
        offer_history = []
        for msg in messages[-self.MAX_CONVERSATION_HISTORY :]:  # Last N messages
            if msg.message_metadata and "counter_offer" in msg.message_metadata:
                offer_history.append(f"${msg.message_metadata['counter_offer']:,.2f}")
            elif msg.message_metadata and "suggested_price" in msg.message_metadata:
                offer_history.append(f"${msg.message_metadata['suggested_price']:,.2f}")

        try:
            # Use centralized LLM client with negotiation agent
            response_content = generate_text(
                prompt_id="negotiation_counter",
                variables={
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "mileage": deal.vehicle_mileage,
                    "asking_price": deal.asking_price,
                    "counter_offer": counter_offer,
                    "round_number": session.current_round,
                    "offer_history": ", ".join(offer_history) if offer_history else "None",
                },
                agent_role="negotiation",
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

            # Get user target price from message history
            user_target = deal.asking_price * self.DEFAULT_TARGET_PRICE_RATIO
            for msg in reversed(messages[-10:]):
                if msg.message_metadata and "target_price" in msg.message_metadata:
                    user_target = msg.message_metadata["target_price"]
                    break

            # Calculate enhanced AI metrics for counter offer
            # Pass the already-fetched messages to avoid redundant query
            ai_metrics = await self._calculate_ai_metrics(
                session_id=session.id,
                deal=deal,
                current_price=new_suggested_price,
                user_target=user_target,
                messages=messages,  # Use already-fetched messages
            )

            return {
                "content": response_content,
                "metadata": {
                    "suggested_price": round(new_suggested_price, 2),
                    "user_counter_offer": counter_offer,
                    "asking_price": deal.asking_price,
                    "financing_options": financing_options,
                    "cash_savings": round(cash_savings, 2) if cash_savings else None,
                    "llm_used": True,
                    **ai_metrics,  # Include all AI intelligence metrics
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

            # Get user target price from previously fetched message history
            # (messages already fetched at the beginning of _generate_counter_response)
            user_target = deal.asking_price * self.DEFAULT_TARGET_PRICE_RATIO
            for msg in reversed(messages[-10:]):
                if msg.message_metadata and "target_price" in msg.message_metadata:
                    user_target = msg.message_metadata["target_price"]
                    break

            # Calculate enhanced AI metrics even for fallback
            # Pass the already-fetched messages to avoid redundant query
            ai_metrics = await self._calculate_ai_metrics(
                session_id=session.id,
                deal=deal,
                current_price=new_suggested_price,
                user_target=user_target,
                messages=messages,  # Use already-fetched messages
            )

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
                    **ai_metrics,  # Include all AI intelligence metrics
                },
            }

    async def get_session_with_messages(self, session_id: int) -> dict[str, Any] | None:
        """
        Get a negotiation session with all its messages

        Args:
            session_id: ID of the negotiation session

        Returns:
            Dictionary with session details and messages, or None if not found
        """
        session = await self.negotiation_repo.get_session(session_id)
        if not session:
            return None

        messages = await self.negotiation_repo.get_messages(session_id)

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
        session =            await self.negotiation_repo.get_session(session_id)
        if not session:
            logger.error(f"[{request_id}] Session {session_id} not found")
            raise ApiError(status_code=404, message=f"Session {session_id} not found")

        # Allow chat even if session is completed/cancelled for post-negotiation questions
        # Get deal
        deal =            await self.deal_repo.get(session.deal_id)
        if not deal:
            logger.error(f"[{request_id}] Deal {session.deal_id} not found")
            raise ApiError(status_code=404, message="Associated deal not found")

        # Add user message
        user_msg =            await self.negotiation_repo.add_message(
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

            agent_response =            await self._generate_chat_response(
                session=session,
                deal=deal,
                user_message=user_message,
                request_id=request_id,
            )

            # Hide typing indicator
            await self.ws_manager.broadcast_typing_indicator(session_id, False)

            agent_msg =            await self.negotiation_repo.add_message(
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
        messages =            await self.negotiation_repo.get_messages(session.id)
        recent_messages = messages[-6:]  # Last 6 messages for context

        conversation_history = []
        for msg in recent_messages:
            role_label = "User" if msg.role == MessageRole.USER else "AI"
            conversation_history.append(f"{role_label}: {msg.content}")

        # Get latest suggested price using helper method
        suggested_price = self._get_latest_suggested_price(session.id, deal.asking_price)

        try:
            # Use centralized LLM client with negotiation agent
            response_content = generate_text(
                prompt_id="negotiation_chat",
                variables={
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "asking_price": deal.asking_price,
                    "current_round": session.current_round,
                    "suggested_price": suggested_price,
                    "status": session.status.value,
                    "conversation_history": "\n".join(conversation_history[-4:]),
                    "user_message": user_message,
                },
                agent_role="negotiation",
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
        session =            await self.negotiation_repo.get_session(session_id)
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
        deal =            await self.deal_repo.get(session.deal_id)
        if not deal:
            logger.error(f"[{request_id}] Deal {session.deal_id} not found")
            raise ApiError(status_code=404, message="Associated deal not found")

        # Add user message with dealer info
        user_msg_content = f"[Dealer Information - {info_type}]\n{content}"
        if price_mentioned:
            user_msg_content += f"\n\nPrice mentioned: ${price_mentioned:,.2f}"

        user_msg =            await self.negotiation_repo.add_message(
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
            agent_response =            await self._generate_dealer_info_analysis(
                session=session,
                deal=deal,
                info_type=info_type,
                content=content,
                price_mentioned=price_mentioned,
                request_id=request_id,
            )

            agent_msg =            await self.negotiation_repo.add_message(
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
        messages =            await self.negotiation_repo.get_messages(session.id)
        user_target = deal.asking_price * self.DEFAULT_TARGET_PRICE_RATIO

        for msg in reversed(messages[-10:]):
            if msg.message_metadata and "target_price" in msg.message_metadata:
                user_target = msg.message_metadata["target_price"]
                break

        try:
            # Use centralized LLM client with evaluator agent for dealer analysis
            response_content = generate_text(
                prompt_id="dealer_info_analysis",
                variables={
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "asking_price": deal.asking_price,
                    "current_round": session.current_round,
                    "suggested_price": suggested_price,
                    "user_target": user_target,
                    "info_type": info_type,
                    "dealer_content": content,
                    "price_mentioned": f"${price_mentioned:,.2f}" if price_mentioned else "None",
                },
                agent_role="evaluator",
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
