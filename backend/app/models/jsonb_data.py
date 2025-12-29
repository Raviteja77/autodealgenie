"""
SQLAlchemy models for data previously stored in MongoDB
Now using PostgreSQL with JSONB columns for flexible schema
"""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.session import Base


class UserPreference(Base):
    """
    User preferences model - stores car search preferences
    Previously stored in MongoDB, now using PostgreSQL JSONB
    """

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)  # User identifier
    preferences = Column(JSONB, nullable=False)  # Flexible preferences structure
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    __table_args__ = (Index("idx_user_preferences_created", "user_id", "created_at"),)

    def __repr__(self):
        return f"<UserPreference {self.id}: User {self.user_id}>"


class SearchHistory(Base):
    """
    Search history model - stores all car search queries
    Previously stored in MongoDB, now using PostgreSQL JSONB
    """

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )  # Nullable for anonymous
    search_criteria = Column(JSONB, nullable=False)  # Search parameters
    result_count = Column(Integer, nullable=False, default=0)
    top_vehicles = Column(JSONB, nullable=True)  # Top vehicle recommendations
    session_id = Column(String(255), nullable=True, index=True)  # Session tracking
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    __table_args__ = (Index("idx_search_history_timestamp", "timestamp"),)

    def __repr__(self):
        return f"<SearchHistory {self.id}: User {self.user_id}, Results {self.result_count}>"


class AIResponse(Base):
    """
    AI response model - stores comprehensive AI interactions
    Previously stored in MongoDB, now using PostgreSQL JSONB
    """

    __tablename__ = "ai_responses"

    id = Column(Integer, primary_key=True, index=True)
    feature = Column(String(50), nullable=False, index=True)  # Feature name
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True, index=True)
    prompt_id = Column(String(100), nullable=False)  # Prompt template ID
    prompt_variables = Column(JSONB, nullable=True)  # Variables substituted
    response_content = Column(JSONB, nullable=False)  # AI-generated response
    response_metadata = Column(JSONB, nullable=True)  # Additional metadata
    model_used = Column(String(100), nullable=True)  # OpenAI model
    tokens_used = Column(Integer, nullable=True)  # Tokens consumed
    temperature = Column(Integer, nullable=True)  # Temperature parameter (stored as int * 100)
    llm_used = Column(Integer, nullable=False, default=1)  # 1 for True, 0 for False
    agent_role = Column(String(50), nullable=True)  # Agent role (research, loan, negotiation, evaluator, qa)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    __table_args__ = (
        Index("idx_ai_responses_feature", "feature", "timestamp"),
        Index("idx_ai_responses_deal", "deal_id", "timestamp"),
        Index("idx_ai_responses_user", "user_id", "timestamp"),
        Index("idx_ai_responses_agent_role", "agent_role", "timestamp"),
    )

    def __repr__(self):
        return f"<AIResponse {self.id}: Feature {self.feature}, Agent {self.agent_role}, Deal {self.deal_id}>"


class MarketCheckQuery(Base):
    """
    MarketCheck API query history model
    Previously stored in MongoDB, now using PostgreSQL JSONB
    Stores query parameters and response summaries for analytics and caching
    """

    __tablename__ = "marketcheck_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_type = Column(String(50), nullable=False, index=True)  # 'search', 'price', 'vin', 'mds'
    params = Column(JSONB, nullable=False)  # Query parameters
    response_summary = Column(JSONB, nullable=False)  # API response summary
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_marketcheck_queries_type", "query_type", "timestamp"),
        Index("idx_marketcheck_queries_user", "user_id", "timestamp"),
    )

    def __repr__(self):
        return f"<MarketCheckQuery {self.id}: Type {self.query_type}, User {self.user_id}>"
