"""Alembic environment script.

Supports both *online* (live DB) and *offline* (SQL generation) modes.
The SQLAlchemy URL is taken from the DATABASE_URL environment variable so
that no credentials are ever stored in source code.
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ── Alembic Config object (gives access to .ini values) ─────────────────────
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Make all ORM models importable so Alembic can detect changes ─────────────
import sys
from pathlib import Path

# Add backend/ to sys.path so that "app.*" imports work.
_backend_dir = Path(__file__).resolve().parents[1]
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from app.database import Base  # noqa: E402  (after sys.path manipulation)

# Import all models so that Base.metadata is populated.
import app.models.user       # noqa: F401, E402
import app.models.chat       # noqa: F401, E402
import app.models.emotion    # noqa: F401, E402

target_metadata = Base.metadata

# ── Override sqlalchemy.url from environment ─────────────────────────────────
_db_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./wellness.db")

# Alembic's sync runners need a *sync* URL, so strip the async driver prefix.
_sync_url = (
    _db_url
    .replace("postgresql+asyncpg://", "postgresql://")
    .replace("sqlite+aiosqlite://", "sqlite://")
)
config.set_main_option("sqlalchemy.url", _sync_url)


# ── Offline mode ─────────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Emit SQL to stdout without an active DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode ──────────────────────────────────────────────────────────────

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations inside it."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        # Use the full async URL for the engine.
        url=_db_url,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Entry point ───────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
