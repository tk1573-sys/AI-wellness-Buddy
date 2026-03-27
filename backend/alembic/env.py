"""Alembic environment configuration.

Reads DATABASE_URL from the environment (or .env) so that the same
configuration works for both development (SQLite) and production
(PostgreSQL).  Async drivers (asyncpg, aiosqlite) are translated to
their synchronous equivalents because Alembic uses a synchronous engine.
"""

from __future__ import annotations

import os
import re
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlalchemy.orm import DeclarativeBase

from alembic import context

# ── make the app importable from within backend/ ─────────────────────────────
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

# ── Import model metadata without triggering the async engine creation ─────
# We must keep the async URL so that create_async_engine in app.database
# succeeds (it validates the driver at import time).  We only convert to
# a sync URL when building the engine for Alembic below.
from app.database import Base  # noqa: E402
import app.models.user  # noqa: E402, F401
import app.models.emotion  # noqa: E402, F401
import app.models.chat  # noqa: E402, F401

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ── helpers ───────────────────────────────────────────────────────────────────

def _sync_url(url: str) -> str:
    """Convert an async driver URL to its synchronous counterpart.

    Alembic uses a sync engine; asyncpg and aiosqlite are async-only.
    """
    url = re.sub(r"\+asyncpg\b", "", url)
    url = re.sub(r"\+aiosqlite\b", "", url)
    return url


def _get_url() -> str:
    """Return the synchronous database URL."""
    raw = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url", "")
    return _sync_url(raw)


# ── offline migrations ────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Emit migration SQL without a live database connection."""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── online migrations ─────────────────────────────────────────────────────────

def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    cfg_section = config.get_section(config.config_ini_section, {})
    cfg_section["sqlalchemy.url"] = _get_url()

    connectable = engine_from_config(
        cfg_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
