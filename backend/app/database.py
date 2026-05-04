"""
Async SQLAlchemy database engine and session factory.

Supports both PostgreSQL (production) and SQLite (development/testing).
The DATABASE_URL setting controls which backend is used.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()
_db_logger = logging.getLogger(__name__)

# PostgreSQL needs an explicit connection pool; SQLite uses its default (StaticPool).
_is_postgres = settings.DATABASE_URL.startswith("postgresql")

_engine_kwargs: dict = {
    "echo": settings.DEBUG,
    "future": True,
}
if _is_postgres:
    _engine_kwargs.update(
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
    )

# Create the async engine.  echo=True is intentionally gated behind DEBUG so
# that SQL is logged only in development.
engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

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
    """Create all tables on startup and ensure the schema is up-to-date.

    Explicitly imports every ORM model so that ``Base.metadata`` is fully
    populated before ``create_all`` runs.  Without this, any model whose
    module has not yet been imported would silently be omitted from the
    created schema.

    Retries up to 3 times with exponential back-off so that a briefly
    unavailable database (e.g. the container is still starting) does not
    prevent the application from eventually connecting.
    """
    import asyncio  # noqa: PLC0415

    # Ensure all ORM models are registered with Base.metadata.
    import app.models.user  # noqa: F401, PLC0415
    import app.models.chat  # noqa: F401, PLC0415
    import app.models.emotion  # noqa: F401, PLC0415
    import app.models.profile  # noqa: F401, PLC0415
    import app.models.guardian_alert  # noqa: F401, PLC0415

    _max_attempts = 3
    for attempt in range(1, _max_attempts + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                # Defensively add any columns that may be missing in pre-existing databases.
                await conn.run_sync(_ensure_emotion_log_columns)
            return
        except Exception as exc:
            if attempt == _max_attempts:
                raise
            _wait = 2 ** attempt  # 2 s, 4 s
            _db_logger.warning(
                "DB init attempt %d/%d failed; retrying in %ds — %s",
                attempt, _max_attempts, _wait, exc,
            )
            await asyncio.sleep(_wait)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session per request.

    Converts SQLAlchemy connectivity errors (OperationalError,
    DisconnectionError, TimeoutError) into HTTP 503 responses so callers
    receive a structured, frontend-friendly error instead of a raw traceback.
    Other DB errors (e.g. IntegrityError) are re-raised as-is.
    """
    import logging as _logging

    from fastapi import HTTPException, status
    from sqlalchemy.exc import DisconnectionError, OperationalError
    from sqlalchemy.exc import TimeoutError as SATimeoutError

    _db_logger = _logging.getLogger(__name__)
    _DB_503_DETAIL = {
        "error": "database_unavailable",
        "message": "The service is temporarily unavailable. Please try again in a moment.",
        "status_code": 503,
    }

    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except (OperationalError, DisconnectionError, SATimeoutError) as exc:
                await session.rollback()
                _db_logger.error("DB connectivity error during request: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=_DB_503_DETAIL,
                ) from exc
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    except HTTPException:
        raise
    except (OperationalError, DisconnectionError, SATimeoutError) as exc:
        _db_logger.error("DB connectivity error when creating session: %s", exc)
        from fastapi import HTTPException, status  # noqa: F811  (already imported above)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_DB_503_DETAIL,
        ) from exc
