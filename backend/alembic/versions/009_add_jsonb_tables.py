"""Add JSONB tables for MongoDB replacement

Revision ID: 009_add_jsonb_tables
Revises: 008_add_performance_indexes
Create Date: 2024-12-27

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = "009_add_jsonb_tables"
down_revision = "008_add_performance_indexes"
branch_labels = None
depends_on = None


def upgrade():
    # Create user_preferences table
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("preferences", JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_preferences_id", "user_preferences", ["id"])
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"])
    op.create_index("idx_user_preferences_created", "user_preferences", ["user_id", "created_at"])

    # Create search_history table
    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("search_criteria", JSONB, nullable=False),
        sa.Column("result_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("top_vehicles", JSONB, nullable=True),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_search_history_id", "search_history", ["id"])
    op.create_index("ix_search_history_user_id", "search_history", ["user_id"])
    op.create_index("ix_search_history_session_id", "search_history", ["session_id"])
    op.create_index("ix_search_history_timestamp", "search_history", ["timestamp"])
    op.create_index("idx_search_history_timestamp", "search_history", ["timestamp"])

    # Create ai_responses table
    op.create_table(
        "ai_responses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("feature", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("deal_id", sa.Integer(), nullable=True),
        sa.Column("prompt_id", sa.String(length=100), nullable=False),
        sa.Column("prompt_variables", JSONB, nullable=True),
        sa.Column("response_content", JSONB, nullable=False),
        sa.Column("response_metadata", JSONB, nullable=True),
        sa.Column("model_used", sa.String(length=100), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("temperature", sa.Integer(), nullable=True),
        sa.Column("llm_used", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["deal_id"],
            ["deals.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_responses_id", "ai_responses", ["id"])
    op.create_index("ix_ai_responses_feature", "ai_responses", ["feature"])
    op.create_index("ix_ai_responses_user_id", "ai_responses", ["user_id"])
    op.create_index("ix_ai_responses_deal_id", "ai_responses", ["deal_id"])
    op.create_index("ix_ai_responses_timestamp", "ai_responses", ["timestamp"])
    op.create_index("idx_ai_responses_feature", "ai_responses", ["feature", "timestamp"])
    op.create_index("idx_ai_responses_deal", "ai_responses", ["deal_id", "timestamp"])
    op.create_index("idx_ai_responses_user", "ai_responses", ["user_id", "timestamp"])


def downgrade():
    # Drop ai_responses table
    op.drop_index("idx_ai_responses_user", table_name="ai_responses")
    op.drop_index("idx_ai_responses_deal", table_name="ai_responses")
    op.drop_index("idx_ai_responses_feature", table_name="ai_responses")
    op.drop_index("ix_ai_responses_timestamp", table_name="ai_responses")
    op.drop_index("ix_ai_responses_deal_id", table_name="ai_responses")
    op.drop_index("ix_ai_responses_user_id", table_name="ai_responses")
    op.drop_index("ix_ai_responses_feature", table_name="ai_responses")
    op.drop_index("ix_ai_responses_id", table_name="ai_responses")
    op.drop_table("ai_responses")

    # Drop search_history table
    op.drop_index("idx_search_history_timestamp", table_name="search_history")
    op.drop_index("ix_search_history_timestamp", table_name="search_history")
    op.drop_index("ix_search_history_session_id", table_name="search_history")
    op.drop_index("ix_search_history_user_id", table_name="search_history")
    op.drop_index("ix_search_history_id", table_name="search_history")
    op.drop_table("search_history")

    # Drop user_preferences table
    op.drop_index("idx_user_preferences_created", table_name="user_preferences")
    op.drop_index("ix_user_preferences_user_id", table_name="user_preferences")
    op.drop_index("ix_user_preferences_id", table_name="user_preferences")
    op.drop_table("user_preferences")
