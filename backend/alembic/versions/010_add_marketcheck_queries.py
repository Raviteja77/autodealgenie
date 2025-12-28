"""Add marketcheck_queries table

Revision ID: 010_add_marketcheck_queries
Revises: 009_add_jsonb_tables
Create Date: 2024-12-28

"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision = "010_add_marketcheck_queries"
down_revision = "009_add_jsonb_tables"
branch_labels = None
depends_on = None


def upgrade():
    # Create marketcheck_queries table
    op.create_table(
        "marketcheck_queries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("query_type", sa.String(length=50), nullable=False),
        sa.Column("params", JSONB, nullable=False),
        sa.Column("response_summary", JSONB, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes for efficient querying
    op.create_index("ix_marketcheck_queries_id", "marketcheck_queries", ["id"])
    op.create_index("ix_marketcheck_queries_query_type", "marketcheck_queries", ["query_type"])
    op.create_index("ix_marketcheck_queries_user_id", "marketcheck_queries", ["user_id"])
    op.create_index("ix_marketcheck_queries_timestamp", "marketcheck_queries", ["timestamp"])
    op.create_index("idx_marketcheck_queries_type", "marketcheck_queries", ["query_type", "timestamp"])
    op.create_index("idx_marketcheck_queries_user", "marketcheck_queries", ["user_id", "timestamp"])


def downgrade():
    # Drop indexes
    op.drop_index("idx_marketcheck_queries_user", "marketcheck_queries")
    op.drop_index("idx_marketcheck_queries_type", "marketcheck_queries")
    op.drop_index("ix_marketcheck_queries_timestamp", "marketcheck_queries")
    op.drop_index("ix_marketcheck_queries_user_id", "marketcheck_queries")
    op.drop_index("ix_marketcheck_queries_query_type", "marketcheck_queries")
    op.drop_index("ix_marketcheck_queries_id", "marketcheck_queries")
    
    # Drop table
    op.drop_table("marketcheck_queries")
