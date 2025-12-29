"""
Repository pattern for Negotiation operations
"""

from typing import Any

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.negotiation import (
    MessageRole,
    NegotiationMessage,
    NegotiationSession,
    NegotiationStatus,
)


class NegotiationRepository:
    """Repository for Negotiation database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        user_id: int,
        deal_id: int,
        max_rounds: int = 10,
    ) -> NegotiationSession:
        """Create a new negotiation session"""
        session = NegotiationSession(
            user_id=user_id,
            deal_id=deal_id,
            max_rounds=max_rounds,
            status=NegotiationStatus.ACTIVE,
            current_round=1,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: int) -> NegotiationSession | None:
        """Get a negotiation session by ID"""
        result = await self.db.execute(
            select(NegotiationSession).filter(NegotiationSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_sessions_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[NegotiationSession]:
        """Get all negotiation sessions for a user"""
        result = await self.db.execute(
            select(NegotiationSession)
            .filter(NegotiationSession.user_id == user_id)
            .order_by(desc(NegotiationSession.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_sessions_by_deal(self, deal_id: int) -> list[NegotiationSession]:
        """Get all negotiation sessions for a deal"""
        result = await self.db.execute(
            select(NegotiationSession)
            .filter(NegotiationSession.deal_id == deal_id)
            .order_by(desc(NegotiationSession.created_at))
        )
        return result.scalars().all()

    async def update_session_status(
        self, session_id: int, status: NegotiationStatus
    ) -> NegotiationSession | None:
        """Update the status of a negotiation session"""
        session = await self.get_session(session_id)
        if not session:
            return None

        session.status = status
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def increment_round(self, session_id: int) -> NegotiationSession | None:
        """Increment the current round of a negotiation session"""
        session = await self.get_session(session_id)
        if not session:
            return None

        session.current_round += 1
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def add_message(
        self,
        session_id: int,
        role: MessageRole,
        content: str,
        round_number: int,
        metadata: dict[str, Any] | None = None,
    ) -> NegotiationMessage:
        """Add a message to a negotiation session"""
        message = NegotiationMessage(
            session_id=session_id,
            role=role,
            content=content,
            round_number=round_number,
            message_metadata=metadata,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_messages(
        self, session_id: int, skip: int = 0, limit: int = 1000
    ) -> list[NegotiationMessage]:
        """Get all messages for a negotiation session"""
        result = await self.db.execute(
            select(NegotiationMessage)
            .filter(NegotiationMessage.session_id == session_id)
            .order_by(asc(NegotiationMessage.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_latest_message(self, session_id: int) -> NegotiationMessage | None:
        """Get the latest message in a negotiation session"""
        result = await self.db.execute(
            select(NegotiationMessage)
            .filter(NegotiationMessage.session_id == session_id)
            .order_by(desc(NegotiationMessage.created_at), desc(NegotiationMessage.id))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def delete_session(self, session_id: int) -> bool:
        """Delete a negotiation session (cascade deletes messages)"""
        session = await self.get_session(session_id)
        if not session:
            return False

        await self.db.delete(session)
        await self.db.commit()
        return True

    def delete_session(self, session_id: int) -> bool:
        """Delete a negotiation session (cascade deletes messages)"""
        session = self.get_session(session_id)
        if not session:
            return False

        self.db.delete(session)
        self.db.commit()
        return True
