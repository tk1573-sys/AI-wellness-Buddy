"""add is_test column to guardian_alerts

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
Create Date: 2026-04-06 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6f7a8b9c0d1'
down_revision: Union[str, Sequence[str], None] = 'd5e6f7a8b9c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_test column to guardian_alerts to distinguish test vs real alerts."""
    op.add_column(
        'guardian_alerts',
        sa.Column('is_test', sa.Boolean(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    """Remove is_test column from guardian_alerts."""
    op.drop_column('guardian_alerts', 'is_test')
