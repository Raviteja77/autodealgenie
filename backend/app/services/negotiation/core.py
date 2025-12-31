import logging
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.negotiation_config import NegotiationConfig
from app.models.negotiation import MessageRole, NegotiationStatus
from app.repositories.ai_response_repository import AIResponseRepository
from app.repositories.deal_repository import DealRepository
from app.repositories.negotiation_repository import NegotiationRepository
from app.services.base_service import BaseService
from app.services.negotiation.financing import FinancingCalculator
from app.services.negotiation.message_handler import NegotiationMessageHandler
from app.services.negotiation.metrics import MetricsCalculator
from app.services.negotiation.response_generator import ResponseGenerator
from app.services.negotiation.session_manager import SessionManager
from app.utils.error_handler import ApiError

if TYPE_CHECKING:
    from app.services.websocket_manager import ConnectionManager

logger = logging.getLogger(__name__)


class NegotiationService(BaseService):
    """Orchestrates negotiation workflow by delegating to specialized modules."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.negotiation_repo = NegotiationRepository(db)
        self.deal_repo = DealRepository(db)
        self.ai_response_repo = AIResponseRepository(db)

        # Initialize delegated modules
        self.metrics = MetricsCalculator(db)
        self.financing = FinancingCalculator()
        self.session_manager = SessionManager(db, self.negotiation_repo)
        self.response_gen = ResponseGenerator()
        self.message_handler = NegotiationMessageHandler(self)

    @property
    def ws_manager(self) -> "ConnectionManager":
        return self.session_manager.ws_manager

    async def create_negotiation(
        self,
        user_id: int,
        deal_id: int,
        user_target_price: float,
        strategy: str | None = None,
        evaluation_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Orchestrates the creation of a negotiation session."""
        request_id = str(uuid.uuid4())
        logger.info(
            f"[{request_id}] Creating negotiation session for user {user_id}, deal {deal_id}"
        )

        deal = await self.deal_repo.get(deal_id)
        if not deal:
            raise ApiError(status_code=404, message=f"Deal with id {deal_id} not found")

        if evaluation_data:
            logger.info(
                f"[{request_id}] Using evaluation data: Fair value: ${evaluation_data.get('fair_value', 'N/A')}"
            )

        session = await self.negotiation_repo.create_session(user_id=user_id, deal_id=deal_id)
        logger.info(f"[{request_id}] Created session {session.id}")

        # Add initial user message
        user_message = (
            f"I'm interested in the {deal.vehicle_year} {deal.vehicle_make} "
            f"{deal.vehicle_model}. The asking price is ${deal.asking_price:,.2f}, "
            f"but my target price is ${user_target_price:,.2f}."
        )
        if strategy:
            user_message += f" My negotiation approach is {strategy}."

        message_metadata = {"target_price": user_target_price, "strategy": strategy}
        if evaluation_data:
            message_metadata["evaluation_data"] = {
                "fair_value": evaluation_data.get("fair_value"),
                "score": evaluation_data.get("score"),
                "has_market_data": bool(evaluation_data.get("market_data")),
            }

        user_msg = await self.negotiation_repo.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content=user_message,
            round_number=1,
            metadata=message_metadata,
        )
        await self.session_manager.broadcast_message(session.id, user_msg)

        # Generate agent response
        try:
            await self.ws_manager.broadcast_typing_indicator(session.id, True)

            agent_response = await self._generate_agent_response(
                session=session,
                deal=deal,
                user_target_price=user_target_price,
                strategy=strategy,
                request_id=request_id,
                evaluation_data=evaluation_data,
            )

            await self.ws_manager.broadcast_typing_indicator(session.id, False)

            agent_msg = await self.negotiation_repo.add_message(
                session_id=session.id,
                role=MessageRole.AGENT,
                content=agent_response["content"],
                round_number=1,
                metadata=agent_response["metadata"],
            )
            await self.session_manager.broadcast_message(session.id, agent_msg)

            logger.info(f"[{request_id}] Session {session.id} initialized successfully")

            return {
                "session_id": session.id,
                "status": session.status.value,
                "current_round": session.current_round,
                "agent_message": agent_response["content"],
                "metadata": agent_response["metadata"],
            }

        except Exception as e:
            await self.db.rollback()
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
        """Process the next round of negotiation."""
        request_id = str(uuid.uuid4())
        logger.info(f"[{request_id}] Processing next round for session {session_id}")

        session = await self.negotiation_repo.get_session(session_id)
        if not session:
            raise ApiError(status_code=404, message=f"Session {session_id} not found")

        if session.status != NegotiationStatus.ACTIVE:
            raise ApiError(
                status_code=400,
                message="Session is not active",
                details={"status": session.status.value},
            )

        if session.current_round >= session.max_rounds:
            await self.negotiation_repo.update_session_status(
                session_id, NegotiationStatus.COMPLETED
            )
            raise ApiError(
                status_code=400,
                message="Maximum negotiation rounds reached",
                details={"max_rounds": session.max_rounds},
            )

        deal = await self.deal_repo.get(session.deal_id)
        if not deal:
            raise ApiError(status_code=404, message="Associated deal not found")

        # Handle user action
        if user_action == "confirm":
            return await self._handle_confirm(session, deal, request_id)
        elif user_action == "reject":
            return await self._handle_reject(session, request_id)
        elif user_action == "counter":
            return await self._handle_counter(session, deal, counter_offer, request_id)
        else:
            raise ApiError(
                status_code=400,
                message="Invalid user action",
                details={"valid_actions": ["confirm", "reject", "counter"]},
            )

    async def _handle_confirm(self, session, deal, request_id: str) -> dict[str, Any]:
        """Handle user confirming the deal."""
        await self.negotiation_repo.update_session_status(session.id, NegotiationStatus.COMPLETED)

        latest_price = await self.session_manager.get_latest_suggested_price(
            session.id, deal.asking_price
        )

        from app.schemas.schemas import DealUpdate

        deal_update = DealUpdate(
            offer_price=latest_price,
            status="completed",
            notes=f"{deal.notes or ''}\nNegotiation completed. Final agreed price: ${latest_price:,.2f}".strip(),
        )
        await self.deal_repo.update(session.deal_id, deal_update)

        message_content = "Thank you! I accept the current offer."
        await self.negotiation_repo.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content=message_content,
            round_number=session.current_round,
            metadata={"action": "confirm"},
        )

        agent_content = (
            "Excellent! The deal is confirmed. We'll proceed with finalizing the paperwork."
        )
        await self.negotiation_repo.add_message(
            session_id=session.id,
            role=MessageRole.AGENT,
            content=agent_content,
            round_number=session.current_round,
            metadata={"action": "deal_confirmed"},
        )

        logger.info(f"[{request_id}] Session {session.id} completed (user confirmed)")
        return {
            "session_id": session.id,
            "status": NegotiationStatus.COMPLETED.value,
            "current_round": session.current_round,
            "agent_message": agent_content,
            "metadata": {"action": "deal_confirmed"},
        }

    async def _handle_reject(self, session, request_id: str) -> dict[str, Any]:
        """Handle user rejecting the negotiation."""
        await self.negotiation_repo.update_session_status(session.id, NegotiationStatus.CANCELLED)

        message_content = "I'm not interested in continuing this negotiation."
        await self.negotiation_repo.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content=message_content,
            round_number=session.current_round,
            metadata={"action": "reject"},
        )

        agent_content = (
            "I understand. Thank you for your time. Feel free to reach out if you change your mind."
        )
        await self.negotiation_repo.add_message(
            session_id=session.id,
            role=MessageRole.AGENT,
            content=agent_content,
            round_number=session.current_round,
            metadata={"action": "negotiation_cancelled"},
        )

        logger.info(f"[{request_id}] Session {session.id} cancelled (user rejected)")
        return {
            "session_id": session.id,
            "status": NegotiationStatus.CANCELLED.value,
            "current_round": session.current_round,
            "agent_message": agent_content,
            "metadata": {"action": "negotiation_cancelled"},
        }

    async def _handle_counter(
        self, session, deal, counter_offer: float | None, request_id: str
    ) -> dict[str, Any]:
        """Handle user making a counter offer."""
        if counter_offer is None or counter_offer <= 0:
            raise ApiError(status_code=400, message="Counter offer is required for counter action")

        session = await self.negotiation_repo.increment_round(session.id)

        message_content = f"I'd like to counter with an offer of ${counter_offer:,.2f}."
        user_msg = await self.negotiation_repo.add_message(
            session_id=session.id,
            role=MessageRole.USER,
            content=message_content,
            round_number=session.current_round,
            metadata={"action": "counter", "counter_offer": counter_offer},
        )
        await self.session_manager.broadcast_message(session.id, user_msg)

        try:
            await self.ws_manager.broadcast_typing_indicator(session.id, True)

            agent_response = await self._generate_counter_response(
                session=session,
                deal=deal,
                counter_offer=counter_offer,
                request_id=request_id,
            )

            await self.ws_manager.broadcast_typing_indicator(session.id, False)

            agent_msg = await self.negotiation_repo.add_message(
                session_id=session.id,
                role=MessageRole.AGENT,
                content=agent_response["content"],
                round_number=session.current_round,
                metadata=agent_response["metadata"],
            )
            await self.session_manager.broadcast_message(session.id, agent_msg)

            logger.info(
                f"[{request_id}] Session {session.id} advanced to round {session.current_round}"
            )

            return {
                "session_id": session.id,
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

    async def get_session_with_messages(self, session_id: int) -> dict[str, Any] | None:
        """Get a negotiation session with all its messages."""
        return await self.session_manager.get_session_with_messages(session_id)

    async def send_chat_message(
        self, session_id: int, user_message: str, message_type: str = "general"
    ) -> dict[str, Any]:
        """Send a free-form chat message and get AI response."""
        request_id = str(uuid.uuid4())

        result = await self.message_handler.handle_chat(
            session_id, user_message, message_type, request_id
        )

        session = result["session"]
        user_msg = result["user_msg"]
        deal = await self.deal_repo.get(session.deal_id)

        try:
            await self.ws_manager.broadcast_typing_indicator(session_id, True)

            agent_response = await self._generate_chat_response(
                session, deal, user_message, request_id
            )

            await self.ws_manager.broadcast_typing_indicator(session_id, False)

            agent_msg = await self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.AGENT,
                content=agent_response["content"],
                round_number=session.current_round,
                metadata={**agent_response["metadata"], "chat_message": True},
            )
            await self.session_manager.broadcast_message(session_id, agent_msg)

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

    async def analyze_dealer_info(
        self,
        session_id: int,
        info_type: str,
        content: str,
        price_mentioned: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze dealer-provided information and provide recommendations."""
        request_id = str(uuid.uuid4())

        result = await self.message_handler.handle_dealer_info(
            session_id, content, info_type, price_mentioned, request_id
        )

        session = result["session"]
        user_msg = result["user_msg"]
        deal = await self.deal_repo.get(session.deal_id)

        try:
            agent_response = await self._generate_dealer_info_analysis(
                session, deal, info_type, content, price_mentioned, request_id
            )

            agent_msg = await self.negotiation_repo.add_message(
                session_id=session_id,
                role=MessageRole.AGENT,
                content=agent_response["content"],
                round_number=session.current_round,
                metadata=agent_response["metadata"],
            )

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

    async def _generate_agent_response(
        self,
        session,
        deal,
        user_target_price: float,
        strategy: str | None,
        request_id: str,
        evaluation_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate agent's initial response using LLM."""
        fair_value = evaluation_data.get("fair_value") if evaluation_data else None
        eval_score = evaluation_data.get("score") if evaluation_data else None

        evaluation_context = "No evaluation data available."
        if evaluation_data:
            evaluation_context = f"Deal Evaluation Results:\n- Fair Market Value: ${fair_value:,.2f}\n- Deal Quality Score: {eval_score}/10\n"
            market_data = evaluation_data.get("market_data") or {}
            if market_data.get("summary"):
                evaluation_context += f"- Market Analysis: {market_data['summary']}\n"

        try:
            response_content = await self.response_gen.generate_initial(
                {
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "mileage": deal.vehicle_mileage,
                    "asking_price": deal.asking_price,
                    "target_price": user_target_price,
                    "strategy": strategy or "Not specified",
                    "evaluation_context": evaluation_context,
                    "fair_value": fair_value or deal.asking_price,
                }
            )

            base_price = fair_value if fair_value else user_target_price
            suggested_price = base_price * (
                0.95
                if fair_value and fair_value < deal.asking_price * 0.9
                else NegotiationConfig.INITIAL_OFFER_MULTIPLIER
            )

            financing_options = self.financing.calculate_financing_options(suggested_price)
            cash_savings = None
            if financing_options:
                baseline = next(
                    (opt for opt in financing_options if opt["loan_term_months"] == 60),
                    financing_options[0],
                )
                if baseline:
                    cash_savings = baseline["total_cost"] - suggested_price

            ai_metrics = await self.metrics._calculate_ai_metrics(
                session.id, deal, suggested_price, user_target_price, None
            )

            try:
                await self.ai_response_repo.create_response(
                    feature="negotiation",
                    user_id=session.user_id,
                    deal_id=deal.id,
                    prompt_id="negotiation_initial",
                    prompt_variables={
                        "user_target_price": user_target_price,
                        "asking_price": deal.asking_price,
                    },
                    response_content=response_content,
                    response_metadata={
                        "suggested_price": suggested_price,
                        "ai_metrics": ai_metrics,
                    },
                    llm_used=True,
                    agent_role="negotiation",
                )
            except Exception as log_error:
                await self.db.rollback()
                logger.error(f"Failed to log AI response: {log_error}")

            return {
                "content": response_content,
                "metadata": {
                    "suggested_price": round(suggested_price, 2),
                    "asking_price": deal.asking_price,
                    "user_target_price": user_target_price,
                    "fair_value": fair_value,
                    "financing_options": financing_options,
                    "cash_savings": round(cash_savings, 2) if cash_savings else None,
                    "llm_used": True,
                    **ai_metrics,
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] LLM call failed: {str(e)}")
            # Fallback logic here (similar to original)
            suggested_price = user_target_price * NegotiationConfig.INITIAL_OFFER_MULTIPLIER
            financing_options = self.financing.calculate_financing_options(suggested_price)
            ai_metrics = await self.metrics._calculate_ai_metrics(
                session.id, deal, suggested_price, user_target_price, None
            )

            fallback_content = f"Thank you for your interest. Your target of ${user_target_price:,.2f} is realistic. I recommend starting lower to give you negotiating room."

            return {
                "content": fallback_content,
                "metadata": {
                    "suggested_price": round(suggested_price, 2),
                    "financing_options": financing_options,
                    "llm_used": False,
                    **ai_metrics,
                },
            }

    async def _generate_counter_response(
        self, session, deal, counter_offer: float, request_id: str
    ) -> dict[str, Any]:
        """Generate agent's counter response."""
        messages = await self.negotiation_repo.get_messages(session.id)
        offer_history = []
        for msg in messages[-NegotiationConfig.MAX_CONVERSATION_HISTORY :]:
            if msg.message_metadata:
                if "counter_offer" in msg.message_metadata:
                    offer_history.append(f"${msg.message_metadata['counter_offer']:,.2f}")
                elif "suggested_price" in msg.message_metadata:
                    offer_history.append(f"${msg.message_metadata['suggested_price']:,.2f}")

        try:
            response_content = await self.response_gen.generate_counter(
                {
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "mileage": deal.vehicle_mileage,
                    "asking_price": deal.asking_price,
                    "counter_offer": counter_offer,
                    "round_number": session.current_round,
                    "offer_history": ", ".join(offer_history) if offer_history else "None",
                }
            )

            price_gap = deal.asking_price - counter_offer
            discount_percent = (price_gap / deal.asking_price) * 100

            if discount_percent >= NegotiationConfig.EXCELLENT_DISCOUNT_THRESHOLD:
                new_suggested_price = counter_offer * NegotiationConfig.HOLD_FIRM_ADJUSTMENT
            elif discount_percent >= NegotiationConfig.GOOD_DISCOUNT_THRESHOLD:
                new_suggested_price = counter_offer * NegotiationConfig.SMALL_INCREASE_ADJUSTMENT
            else:
                new_suggested_price = (
                    counter_offer * NegotiationConfig.AGGRESSIVE_DECREASE_ADJUSTMENT
                )

            financing_options = self.financing.calculate_financing_options(new_suggested_price)

            user_target = deal.asking_price * NegotiationConfig.DEFAULT_TARGET_PRICE_RATIO
            for msg in reversed(messages[-10:]):
                if msg.message_metadata and "target_price" in msg.message_metadata:
                    user_target = msg.message_metadata["target_price"]
                    break

            ai_metrics = await self.metrics._calculate_ai_metrics(
                session.id, deal, new_suggested_price, user_target, messages
            )

            return {
                "content": response_content,
                "metadata": {
                    "suggested_price": round(new_suggested_price, 2),
                    "user_counter_offer": counter_offer,
                    "financing_options": financing_options,
                    "llm_used": True,
                    **ai_metrics,
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] LLM call failed: {str(e)}")
            # Fallback logic
            return {"content": "Fallback response", "metadata": {"llm_used": False}}

    async def _generate_chat_response(
        self, session, deal, user_message: str, request_id: str
    ) -> dict[str, Any]:
        """Generate AI response to free-form chat."""
        messages = await self.negotiation_repo.get_messages(session.id)
        conversation_history = []
        for msg in messages[-6:]:
            role_label = "User" if msg.role == MessageRole.USER else "AI"
            conversation_history.append(f"{role_label}: {msg.content}")

        suggested_price = await self.session_manager.get_latest_suggested_price(
            session.id, deal.asking_price
        )

        try:
            response_content = await self.response_gen.generate_chat(
                {
                    "make": deal.vehicle_make,
                    "model": deal.vehicle_model,
                    "year": deal.vehicle_year,
                    "asking_price": deal.asking_price,
                    "current_round": session.current_round,
                    "suggested_price": suggested_price,
                    "status": session.status.value,
                    "conversation_history": "\n".join(conversation_history[-4:]),
                    "user_message": user_message,
                }
            )

            return {
                "content": response_content,
                "metadata": {"llm_used": True, "message_type": "chat_response"},
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

    async def _generate_dealer_info_analysis(
        self,
        session,
        deal,
        info_type: str,
        content: str,
        price_mentioned: float | None,
        request_id: str,
    ) -> dict[str, Any]:
        """Generate AI analysis of dealer info."""
        suggested_price = await self.session_manager.get_latest_suggested_price(
            session.id, deal.asking_price
        )

        messages = await self.negotiation_repo.get_messages(session.id)
        user_target = deal.asking_price * NegotiationConfig.DEFAULT_TARGET_PRICE_RATIO
        for msg in reversed(messages[-10:]):
            if msg.message_metadata and "target_price" in msg.message_metadata:
                user_target = msg.message_metadata["target_price"]
                break

        try:
            response_content = await self.response_gen.generate_dealer_analysis(
                {
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
                }
            )

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
                    "recommended_action": recommended_action,
                },
            }

        except Exception as e:
            logger.error(f"[{request_id}] LLM call failed: {str(e)}")
            return {
                "content": "Fallback dealer analysis",
                "metadata": {"llm_used": False, "fallback": True},
            }
