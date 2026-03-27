"""add user_profiles table

Revision ID: a1b2c3d4e5f6
Revises: 82dd7aace83d
Create Date: 2026-03-27 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '82dd7aace83d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user_profiles table."""
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=50), nullable=True),
        sa.Column('occupation', sa.String(length=200), nullable=True),
        sa.Column('stress_level', sa.Integer(), nullable=True),
        sa.Column('sleep_pattern', sa.String(length=100), nullable=True),
        sa.Column('triggers', sa.JSON(), nullable=True),
        sa.Column('personality_type', sa.String(length=100), nullable=True),
        sa.Column('baseline_emotion', sa.String(length=50), nullable=True),
        sa.Column('exercise_frequency', sa.String(length=100), nullable=True),
        sa.Column('social_support', sa.String(length=100), nullable=True),
        sa.Column('coping_strategies', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index(op.f('ix_user_profiles_id'), 'user_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_user_profiles_user_id'), 'user_profiles', ['user_id'], unique=True)


def downgrade() -> None:
    """Remove user_profiles table."""
    op.drop_index(op.f('ix_user_profiles_user_id'), table_name='user_profiles')
    op.drop_index(op.f('ix_user_profiles_id'), table_name='user_profiles')
    op.drop_table('user_profiles')
