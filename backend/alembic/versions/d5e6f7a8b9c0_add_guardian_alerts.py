"""add guardian alert settings and guardian_alerts table

Revision ID: d5e6f7a8b9c0
Revises: c3d4e5f6a7b8
Create Date: 2026-04-06 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5e6f7a8b9c0'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add guardian settings columns to user_profiles and create guardian_alerts table."""

    # --- guardian settings on user_profiles ---
    op.add_column('user_profiles', sa.Column('enable_guardian_alerts', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user_profiles', sa.Column('guardian_consent_given', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('user_profiles', sa.Column('guardian_name', sa.String(length=200), nullable=True))
    op.add_column('user_profiles', sa.Column('guardian_email', sa.String(length=255), nullable=True))
    op.add_column('user_profiles', sa.Column('guardian_whatsapp', sa.String(length=50), nullable=True))
    op.add_column('user_profiles', sa.Column('guardian_relationship', sa.String(length=100), nullable=True))

    # --- guardian_alerts log table ---
    op.create_table(
        'guardian_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False),
        sa.Column('risk_reason', sa.Text(), nullable=True),
        sa.Column('channel', sa.String(length=20), nullable=False),
        sa.Column('delivery_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_guardian_alerts_id'), 'guardian_alerts', ['id'], unique=False)
    op.create_index(op.f('ix_guardian_alerts_user_id'), 'guardian_alerts', ['user_id'], unique=False)


def downgrade() -> None:
    """Remove guardian alerts table and settings columns."""
    op.drop_index(op.f('ix_guardian_alerts_user_id'), table_name='guardian_alerts')
    op.drop_index(op.f('ix_guardian_alerts_id'), table_name='guardian_alerts')
    op.drop_table('guardian_alerts')

    op.drop_column('user_profiles', 'guardian_relationship')
    op.drop_column('user_profiles', 'guardian_whatsapp')
    op.drop_column('user_profiles', 'guardian_email')
    op.drop_column('user_profiles', 'guardian_name')
    op.drop_column('user_profiles', 'guardian_consent_given')
    op.drop_column('user_profiles', 'enable_guardian_alerts')
