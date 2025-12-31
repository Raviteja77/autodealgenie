import logging

from app.models.negotiation import MessageRole, NegotiationStatus
from app.utils.error_handler import NegotiationError

logger = logging.getLogger(__name__)


class NegotiationMessageHandler:
    """Handles different communication types within a negotiation session."""

    def __init__(self, service):
        """
        Args:
            service: An instance of NegotiationService to access repos and broadcasting.
        """
        self.service = service

    async def handle_chat(
        self, session_id: int, user_message: str, message_type: str, request_id: str
    ) -> dict:
        """Processes free-form user chat messages and triggers AI response."""
        session = await self.service.negotiation_repo.get_session(session_id)
        if not session:
            raise NegotiationError(message=f"Session {session_id} not found")

        # 1. Persist the user's message
        user_msg = await self.service.negotiation_repo.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=user_message,
            round_number=session.current_round,
            metadata={"message_type": message_type, "chat_message": True},
        )

        # 2. Broadcast via WebSocket
        await self.service.session_manager.broadcast_message(session_id, user_msg)

        # 3. Generate and return response metadata (handled in core/generators)
        return {"user_msg": user_msg, "session": session}

    async def handle_dealer_info(
        self,
        session_id: int,
        content: str,
        info_type: str,
        price_mentioned: float | None,
        request_id: str,
    ) -> dict:
        """Processes and analyzes information provided by a dealer."""
        session = await self.service.negotiation_repo.get_session(session_id)
        if not session or session.status != NegotiationStatus.ACTIVE:
            raise NegotiationError(message="Active session required for dealer analysis")

        user_msg_content = f"[Dealer Information - {info_type}]\n{content}"
        if price_mentioned:
            user_msg_content += f"\n\nPrice mentioned: ${price_mentioned:,.2f}"

        user_msg = await self.service.negotiation_repo.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=user_msg_content,
            round_number=session.current_round,
            metadata={
                "message_type": "dealer_info",
                "info_type": info_type,
                "price_mentioned": price_mentioned,
            },
        )
        return {"user_msg": user_msg, "session": session}
