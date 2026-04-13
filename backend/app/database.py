"""
Async SQLAlchemy database engine and session factory.

Supports both PostgreSQL (production) and SQLite (development/testing).
The DATABASE_URL setting controls which backend is used.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# Create the async engine.  echo=True is intentionally gated behind DEBUG so
# that SQL is logged only in development.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


_REQUIRED_EMOTION_LOG_COLUMNS: tuple[str, ...] = (
    "risk_score",
    "personalization_score",
)


def _ensure_emotion_log_columns(conn: "sqlalchemy.engine.Connection") -> None:
    """Add missing columns to emotion_logs if they are absent (safe ALTER TABLE).

    This handles databases that were created before the risk_score /
    personalization_score columns were introduced, without requiring a
    full Alembic migration to be run manually.
    """
    from sqlalchemy import inspect, text  # local import to keep top-level clean

    inspector = inspect(conn)
    if "emotion_logs" not in inspector.get_table_names():
        # Table doesn't exist yet — create_all will handle it with the full schema.
        return

    existing = {col["name"] for col in inspector.get_columns("emotion_logs")}
    for col_name in _REQUIRED_EMOTION_LOG_COLUMNS:
        # col_name is drawn from the fixed tuple above — not user input.
        assert col_name.replace("_", "").isalpha(), f"Unexpected column name: {col_name!r}"
        if col_name not in existing:
            conn.execute(
                text(
                    f"ALTER TABLE emotion_logs"
                    f" ADD COLUMN {col_name} FLOAT NOT NULL DEFAULT 0.0"
                )
            )


async def init_db() -> None:
    """Create all tables on startup and ensure the schema is up-to-date."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Defensively add any columns that may be missing in pre-existing databases.
        await conn.run_sync(_ensure_emotion_log_columns)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
