"""
Async SQLAlchemy database engine and session factory.

Supports both PostgreSQL (production) and SQLite (development/testing).
The DATABASE_URL setting controls which backend is used.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

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


async def run_migrations() -> None:
    """Apply pending Alembic migrations (idempotent on every startup)."""
    import asyncio
    from alembic import command
    from alembic.config import Config

    _alembic_cfg_path = Path(__file__).resolve().parents[1] / "alembic.ini"

    def _run() -> None:
        cfg = Config(str(_alembic_cfg_path))
        command.upgrade(cfg, "head")

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _run)
    logger.info("Alembic migrations applied.")


# Keep init_db for backwards-compatibility in tests that use SQLite.
async def init_db() -> None:
    """Create all tables on startup (idempotent). Used by test suite."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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
