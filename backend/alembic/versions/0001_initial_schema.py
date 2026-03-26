"""Initial schema: users, chat_history, emotion_logs

Revision ID: 0001
Revises:
Create Date: 2026-03-26 21:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # ── chat_history ────────────────────────────────────────────────────────
    op.create_table(
        "chat_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("emotion", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chat_history_id"), "chat_history", ["id"], unique=False)
    op.create_index(op.f("ix_chat_history_user_id"), "chat_history", ["user_id"], unique=False)
    op.create_index(op.f("ix_chat_history_session_id"), "chat_history", ["session_id"], unique=False)

    # ── emotion_logs ────────────────────────────────────────────────────────
    op.create_table(
        "emotion_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("input_text", sa.String(length=2000), nullable=False),
        sa.Column("primary_emotion", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("uncertainty", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("is_high_risk", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("all_scores", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_emotion_logs_id"), "emotion_logs", ["id"], unique=False)
    op.create_index(op.f("ix_emotion_logs_user_id"), "emotion_logs", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_emotion_logs_user_id"), table_name="emotion_logs")
    op.drop_index(op.f("ix_emotion_logs_id"), table_name="emotion_logs")
    op.drop_table("emotion_logs")

    op.drop_index(op.f("ix_chat_history_session_id"), table_name="chat_history")
    op.drop_index(op.f("ix_chat_history_user_id"), table_name="chat_history")
    op.drop_index(op.f("ix_chat_history_id"), table_name="chat_history")
    op.drop_table("chat_history")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
