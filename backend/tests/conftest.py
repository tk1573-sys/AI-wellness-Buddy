"""Pytest configuration for backend tests.

Sets up an in-memory SQLite database and async test client for every test
session.  The AI modules in the project root are added to sys.path so that
service imports work without installation.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# ── make project-root AI modules importable ──────────────────────────────────
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Offline mode so tests never call the HuggingFace Hub
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

# Use an in-memory SQLite database for all tests
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough-for-jwt"
# Disable rate limiting so tests don't hit per-IP limits
os.environ["RATELIMIT_ENABLED"] = "false"

# ── import after env is set ───────────────────────────────────────────────────
from app.database import Base, get_db  # noqa: E402
from app.main import create_app  # noqa: E402

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine):
    """Yield a fresh session, rolled back after each test."""
    AsyncTestSession = async_sessionmaker(async_engine, expire_on_commit=False)
    async with AsyncTestSession() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(async_engine):
    """Async HTTP test client wired to an in-memory DB."""
    app = create_app()

    AsyncTestSession = async_sessionmaker(async_engine, expire_on_commit=False)

    async def override_get_db():
        async with AsyncTestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
