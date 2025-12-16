"""
Repository pattern for Negotiation operations
"""

from typing import Any

from sqlalchemy.orm import Session

from app.models.negotiation import (
    MessageRole,
    NegotiationMessage,
    NegotiationSession,
    NegotiationStatus,
)


class NegotiationRepository:
    """Repository for Negotiation database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_session(
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
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: int) -> NegotiationSession | None:
        """Get a negotiation session by ID"""
        return (
            self.db.query(NegotiationSession)
            .filter(NegotiationSession.id == session_id)
            .first()
        )

    def get_sessions_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[NegotiationSession]:
        """Get all negotiation sessions for a user"""
        return (
            self.db.query(NegotiationSession)
            .filter(NegotiationSession.user_id == user_id)
            .order_by(NegotiationSession.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_sessions_by_deal(self, deal_id: int) -> list[NegotiationSession]:
        """Get all negotiation sessions for a deal"""
        return (
            self.db.query(NegotiationSession)
            .filter(NegotiationSession.deal_id == deal_id)
            .order_by(NegotiationSession.created_at.desc())
            .all()
        )

    def update_session_status(
        self, session_id: int, status: NegotiationStatus
    ) -> NegotiationSession | None:
        """Update the status of a negotiation session"""
        session = self.get_session(session_id)
        if not session:
            return None

        session.status = status
        self.db.commit()
        self.db.refresh(session)
        return session

    def increment_round(self, session_id: int) -> NegotiationSession | None:
        """Increment the current round of a negotiation session"""
        session = self.get_session(session_id)
        if not session:
            return None

        session.current_round += 1
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(
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
            metadata=metadata,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_messages(
        self, session_id: int, skip: int = 0, limit: int = 1000
    ) -> list[NegotiationMessage]:
        """Get all messages for a negotiation session"""
        return (
            self.db.query(NegotiationMessage)
            .filter(NegotiationMessage.session_id == session_id)
            .order_by(NegotiationMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_message(self, session_id: int) -> NegotiationMessage | None:
        """Get the latest message in a negotiation session"""
        return (
            self.db.query(NegotiationMessage)
            .filter(NegotiationMessage.session_id == session_id)
            .order_by(NegotiationMessage.created_at.desc())
            .first()
        )

    def delete_session(self, session_id: int) -> bool:
        """Delete a negotiation session (cascade deletes messages)"""
        session = self.get_session(session_id)
        if not session:
            return False

        self.db.delete(session)
        self.db.commit()
        return True
