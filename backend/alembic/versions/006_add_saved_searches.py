"""Add saved_searches table

Revision ID: 006_add_saved_searches
Revises: 005_add_favorites
Create Date: 2025-12-20 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "006_add_saved_searches"
down_revision = "005_add_favorites"
branch_labels = None
depends_on = None


def upgrade():
    # Create saved_searches table
    op.create_table(
        "saved_searches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("make", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("budget_min", sa.Float(), nullable=True),
        sa.Column("budget_max", sa.Float(), nullable=True),
        sa.Column("car_type", sa.String(length=50), nullable=True),
        sa.Column("year_min", sa.Integer(), nullable=True),
        sa.Column("year_max", sa.Integer(), nullable=True),
        sa.Column("mileage_max", sa.Integer(), nullable=True),
        sa.Column("fuel_type", sa.String(length=50), nullable=True),
        sa.Column("transmission", sa.String(length=50), nullable=True),
        sa.Column("condition", sa.String(length=50), nullable=True),
        sa.Column("user_priorities", sa.Text(), nullable=True),
        sa.Column("notification_enabled", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("last_checked", sa.DateTime(timezone=True), nullable=True),
        sa.Column("new_matches_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("ix_saved_searches_id", "saved_searches", ["id"])
    op.create_index("ix_saved_searches_user_id", "saved_searches", ["user_id"])


def downgrade():
    # Drop indexes
    op.drop_index("ix_saved_searches_user_id", table_name="saved_searches")
    op.drop_index("ix_saved_searches_id", table_name="saved_searches")

    # Drop table
    op.drop_table("saved_searches")
