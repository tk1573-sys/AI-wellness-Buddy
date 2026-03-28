"""add risk_score and personalization_score to emotion_logs

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-03-28 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add risk_score and personalization_score columns to emotion_logs."""
    op.add_column(
        'emotion_logs',
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
    )
    op.add_column(
        'emotion_logs',
        sa.Column('personalization_score', sa.Float(), nullable=False, server_default='0.0'),
    )


def downgrade() -> None:
    """Remove risk_score and personalization_score from emotion_logs."""
    op.drop_column('emotion_logs', 'personalization_score')
    op.drop_column('emotion_logs', 'risk_score')
