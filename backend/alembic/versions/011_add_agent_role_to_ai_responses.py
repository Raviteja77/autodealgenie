"""add_agent_role_to_ai_responses

Revision ID: 011_add_agent_role
Revises: 010_add_marketcheck_queries
Create Date: 2024-12-29 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011_add_agent_role'
down_revision = '010_add_marketcheck_queries'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add agent_role column to ai_responses table for tracking which agent handled the request"""
    # Add agent_role column (nullable initially to avoid issues with existing rows)
    op.add_column('ai_responses', sa.Column('agent_role', sa.String(length=50), nullable=True))
    
    # Create index on agent_role for better query performance
    op.create_index(
        'idx_ai_responses_agent_role',
        'ai_responses',
        ['agent_role', 'timestamp'],
        unique=False
    )


def downgrade() -> None:
    """Remove agent_role column from ai_responses table"""
    # Drop index first
    op.drop_index('idx_ai_responses_agent_role', table_name='ai_responses')
    
    # Drop column
    op.drop_column('ai_responses', 'agent_role')
