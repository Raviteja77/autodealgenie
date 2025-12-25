"""
WebSocket Connection Manager for Real-Time Negotiation Chat
"""

import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time negotiation chat"""

    def __init__(self):
        # Maps session_id to list of active WebSocket connections
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: int):
        """
        Accept a new WebSocket connection for a negotiation session

        Args:
            websocket: WebSocket connection
            session_id: Negotiation session ID
        """
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(
            f"New WebSocket connection for session {session_id}. "
            f"Total connections: {len(self.active_connections[session_id])}"
        )

    def disconnect(self, websocket: WebSocket, session_id: int):
        """
        Remove a WebSocket connection

        Args:
            websocket: WebSocket connection to remove
            session_id: Negotiation session ID
        """
        if session_id in self.active_connections:
            try:
                self.active_connections[session_id].remove(websocket)
                logger.info(
                    f"WebSocket disconnected for session {session_id}. "
                    f"Remaining connections: {len(self.active_connections[session_id])}"
                )

                # Clean up empty session lists
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
            except ValueError:
                # Connection already removed
                pass

    async def send_message(self, session_id: int, message: dict):
        """
        Send a message to all connected clients for a session

        Args:
            session_id: Negotiation session ID
            message: Message dictionary to send
        """
        if session_id not in self.active_connections:
            logger.debug(f"No active connections for session {session_id}")
            return

        disconnected = []
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, session_id)

    async def broadcast_typing_indicator(self, session_id: int, is_typing: bool):
        """
        Broadcast typing indicator to all connected clients

        Args:
            session_id: Negotiation session ID
            is_typing: Whether AI is currently typing
        """
        await self.send_message(
            session_id,
            {
                "type": "typing_indicator",
                "is_typing": is_typing,
            },
        )

    async def broadcast_message(self, session_id: int, message_data: dict):
        """
        Broadcast a new message to all connected clients

        Args:
            session_id: Negotiation session ID
            message_data: Message data to broadcast
        """
        await self.send_message(
            session_id,
            {
                "type": "new_message",
                "message": message_data,
            },
        )

    async def broadcast_error(self, session_id: int, error: str):
        """
        Broadcast an error to all connected clients

        Args:
            session_id: Negotiation session ID
            error: Error message
        """
        await self.send_message(
            session_id,
            {
                "type": "error",
                "error": error,
            },
        )

    def get_connection_count(self, session_id: int) -> int:
        """
        Get the number of active connections for a session

        Args:
            session_id: Negotiation session ID

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(session_id, []))


# Global connection manager instance
connection_manager = ConnectionManager()
