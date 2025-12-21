"""
Negotiation service with LLM integration for multi-round negotiations
"""

import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.llm import generate_text
from app.models.negotiation import MessageRole, NegotiationSession, NegotiationStatus
from app.repositories.deal_repository import DealRepository
from app.repositories.negotiation_repository import NegotiationRepository
from app.services.loan_calculator_service import LoanCalculatorService
from app.utils.error_handler import ApiError

logger = logging.getLogger(__name__)


class NegotiationService:
    """Service for managing multi-round negotiations with LLM"""

    MAX_CONVERSATION_HISTORY = 4  # Number of recent messages to include in context
    DEFAULT_DOWN_PAYMENT_PERCENT = 0.10  # 10% down payment
    DEFAULT_CREDIT_SCORE_RANGE = "good"  # Default credit range for calculations

    def __init__(self, db: Session):
        self.db = db
        self.negotiation_repo = NegotiationRepository(db)
        self.deal_repo = DealRepository(db)

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

        self.negotiation_repo.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content=user_message,
            round_number=1,
            metadata={"target_price": user_target_price, "strategy": strategy},
        )

        # Generate agent's initial response using LLM
        try:
            agent_response = await self._generate_agent_response(
                session=session,
                deal=deal,
                user_target_price=user_target_price,
                strategy=strategy,
                request_id=request_id,
            )

            self.negotiation_repo.add_message(
                session_id=session.id,
                role=MessageRole.AGENT,
                content=agent_response["content"],
                round_number=1,
                metadata=agent_response["metadata"],
            )

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
            self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=message_content,
                round_number=session.current_round,
                metadata={"action": "counter", "counter_offer": counter_offer},
            )

            # Generate agent's counter response using LLM
            try:
                agent_response = await self._generate_counter_response(
                    session=session,
                    deal=deal,
                    counter_offer=counter_offer,
                    request_id=request_id,
                )

                self.negotiation_repo.add_message(
                    session_id=session_id,
                    role=MessageRole.AGENT,
                    content=agent_response["content"],
                    round_number=session.current_round,
                    metadata=agent_response["metadata"],
                )

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
            response_content = await generate_text(
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

            # Generate suggested counter offer (simple logic for now)
            price_difference = deal.asking_price - user_target_price
            suggested_price = user_target_price + (price_difference * 0.5)

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
                f"I see you're looking for ${user_target_price:,.2f}, "
                f"while the asking price is ${deal.asking_price:,.2f}. "
                f"Let me work on finding a middle ground that works for both parties."
            )

            price_difference = deal.asking_price - user_target_price
            suggested_price = user_target_price + (price_difference * 0.5)

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
            response_content = await generate_text(
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

            # Generate new suggested price (converge toward asking price)
            price_difference = deal.asking_price - counter_offer
            convergence_rate = 1 - (session.current_round / session.max_rounds)
            new_suggested_price = counter_offer + (price_difference * convergence_rate * 0.6)

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
            # Fallback response
            price_difference = deal.asking_price - counter_offer
            convergence_rate = 1 - (session.current_round / session.max_rounds)
            new_suggested_price = counter_offer + (price_difference * convergence_rate * 0.6)

            fallback_content = (
                f"I appreciate your offer of ${counter_offer:,.2f}. "
                f"While I understand your position, the asking price is ${deal.asking_price:,.2f}. "
                f"How about we meet closer to ${new_suggested_price:,.2f}? "
                f"This takes into account the vehicle's condition and market value."
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
