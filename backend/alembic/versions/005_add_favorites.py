"""Add favorites table

Revision ID: 005_add_favorites
Revises: 004_add_deal_evaluations
Create Date: 2025-12-19 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "005_add_favorites"
down_revision = "004_add_deal_evaluations"
branch_labels = None
depends_on = None


def upgrade():
    # Create favorites table
    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("vin", sa.String(length=17), nullable=False),
        sa.Column("make", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("mileage", sa.Integer(), nullable=True),
        sa.Column("fuel_type", sa.String(length=50), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("color", sa.String(length=50), nullable=True),
        sa.Column("condition", sa.String(length=50), nullable=True),
        sa.Column("image", sa.String(length=512), nullable=True),
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
    op.create_index("ix_favorites_id", "favorites", ["id"])
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"])
    op.create_index("ix_favorites_vin", "favorites", ["vin"])

    # Create unique constraint on user_id + vin to prevent duplicates
    op.create_index("ix_favorites_user_vin", "favorites", ["user_id", "vin"], unique=True)


def downgrade():
    # Drop indexes
    op.drop_index("ix_favorites_user_vin", table_name="favorites")
    op.drop_index("ix_favorites_vin", table_name="favorites")
    op.drop_index("ix_favorites_user_id", table_name="favorites")
    op.drop_index("ix_favorites_id", table_name="favorites")

    # Drop table
    op.drop_table("favorites")
