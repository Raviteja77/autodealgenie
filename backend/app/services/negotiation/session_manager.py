# session_manager.py
import logging
from typing import TYPE_CHECKING, Any

from app.repositories.negotiation_repository import NegotiationRepository

if TYPE_CHECKING:
    from app.services.websocket_manager import ConnectionManager

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session retrieval, WebSocket broadcasting, and session utilities."""

    def __init__(self, db, negotiation_repo: NegotiationRepository):
        self.db = db
        self.negotiation_repo = negotiation_repo
        self._ws_manager = None

    @property
    def ws_manager(self) -> "ConnectionManager":
        if self._ws_manager is None:
            from app.services.websocket_manager import connection_manager

            self._ws_manager = connection_manager
        return self._ws_manager

    async def broadcast_message(self, session_id: int, message: Any):
        """Broadcast a message via WebSocket to all connected clients."""
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

    async def get_latest_suggested_price(self, session_id: int, default_price: float) -> float:
        """Get the latest suggested price from message history."""
        messages = await self.negotiation_repo.get_messages(session_id)
        for msg in reversed(messages[-10:]):
            if msg.message_metadata and "suggested_price" in msg.message_metadata:
                return msg.message_metadata["suggested_price"]
        return default_price

    async def get_session_with_messages(self, session_id: int) -> dict[str, Any] | None:
        """Get a negotiation session with all its messages."""
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
