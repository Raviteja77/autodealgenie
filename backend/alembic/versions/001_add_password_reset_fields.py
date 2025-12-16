"""Add password reset fields to User model

Revision ID: 001_add_password_reset_fields
Revises:
Create Date: 2025-12-14 22:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_add_password_reset_fields"
down_revision: str | None = "000_initial_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add reset_token and reset_token_expires columns to users table"""
    op.add_column("users", sa.Column("reset_token", sa.String(length=255), nullable=True))
    op.add_column(
        "users", sa.Column("reset_token_expires", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Remove reset_token and reset_token_expires columns from users table"""
    op.drop_column("users", "reset_token_expires")
    op.drop_column("users", "reset_token")
