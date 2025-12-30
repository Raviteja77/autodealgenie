"""add pgvector and embeddings

Revision ID: 012_add_pgvector_and_embeddings
Revises: 011_add_agent_role
Create Date: 2025-12-30 01:17:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "012_add_pgvector_and_embeddings"
down_revision: str | None = "011_add_agent_role"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enable pgvector extension and add embedding columns"""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Add embedding column to negotiation_sessions for vector similarity search
    # Using 1536 dimensions for OpenAI text-embedding-3-small model
    dimension = 1536
    op.add_column(
        "negotiation_sessions",
        sa.Column("session_embedding", VECTOR(dimension), nullable=True),
    )

    # Add embedding column to negotiation_messages
    op.add_column(
        "negotiation_messages",
        sa.Column("message_embedding", VECTOR(dimension), nullable=True),
    )

    # Create indexes for vector similarity search
    # Note: Using cosine distance for semantic similarity
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_negotiation_sessions_embedding
        ON negotiation_sessions USING ivfflat (session_embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_negotiation_messages_embedding
        ON negotiation_messages USING ivfflat (message_embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )

    # Add negotiation analytics metadata table for ML model results
    op.create_table(
        "negotiation_analytics",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "session_id",
            sa.Integer(),
            sa.ForeignKey("negotiation_sessions.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("success_probability", sa.Float(), nullable=True),
        sa.Column("predicted_outcome", sa.String(50), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("optimal_counter_offer", sa.Float(), nullable=True),
        sa.Column("market_position_score", sa.Float(), nullable=True),
        sa.Column("negotiation_patterns", sa.JSON(), nullable=True),
        sa.Column("similar_session_ids", sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Add index for fast lookups
    op.create_index(
        "idx_negotiation_analytics_session_id",
        "negotiation_analytics",
        ["session_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove pgvector extension and embedding columns"""
    # Drop negotiation analytics table
    op.drop_index("idx_negotiation_analytics_session_id", table_name="negotiation_analytics")
    op.drop_table("negotiation_analytics")

    # Drop vector indexes
    op.execute("DROP INDEX IF EXISTS idx_negotiation_messages_embedding")
    op.execute("DROP INDEX IF EXISTS idx_negotiation_sessions_embedding")

    # Drop embedding columns
    op.drop_column("negotiation_messages", "message_embedding")
    op.drop_column("negotiation_sessions", "session_embedding")

    # Note: We don't drop the vector extension in downgrade as it might be used by other tables
    # op.execute("DROP EXTENSION IF EXISTS vector")
