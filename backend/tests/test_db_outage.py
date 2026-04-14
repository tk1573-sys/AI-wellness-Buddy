"""Tests for graceful DB outage handling across critical routes.

When the database is unavailable (SQLAlchemy OperationalError /
DisconnectionError / TimeoutError), every critical endpoint must:
  - return HTTP 503
  - return a structured JSON body (no raw traceback)
  - include a frontend-friendly "message" field
"""

from __future__ import annotations

import pytest
from sqlalchemy.exc import OperationalError

pytestmark = pytest.mark.asyncio

# ── helpers ──────────────────────────────────────────────────────────────────

_503_ROUTES = [
    # (method, path, json_body)
    ("POST", "/api/v1/auth/signup", {"email": "x@x.com", "username": "xuser", "password": "Passw0rd!"}),
    ("POST", "/api/v1/auth/login", {"email": "x@x.com", "password": "Passw0rd!"}),
    ("GET",  "/api/v1/auth/me",   None),
    ("POST", "/api/v1/chat",      {"message": "hello"}),
    ("GET",  "/api/v1/chat/history", None),
    ("GET",  "/api/v1/dashboard", None),
    ("GET",  "/api/v1/journey",   None),
    ("GET",  "/api/v1/weekly-report", None),
    ("POST", "/api/v1/guardian-alert", {"risk_level": "high", "risk_reason": "test"}),
    ("GET",  "/api/v1/guardian-alert", None),
]

_BEARER = {"Authorization": "Bearer any-token"}


def _make_broken_db():
    """Return an async generator that raises OperationalError immediately."""
    async def broken_db():
        raise OperationalError("connection refused", None, None)
        yield  # make it a generator  # noqa: unreachable
    return broken_db


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def outage_client(async_engine):
    """HTTP client whose get_db dependency always raises OperationalError."""
    import pytest_asyncio  # noqa: F401 — ensures async fixture resolution

    async def _inner():
        from httpx import ASGITransport, AsyncClient
        from sqlalchemy.ext.asyncio import async_sessionmaker

        from app.database import get_db
        from app.main import create_app

        app = create_app()
        app.dependency_overrides[get_db] = _make_broken_db()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    return _inner


# ── parametrised test ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("method,path,body", _503_ROUTES)
async def test_route_returns_503_on_db_outage(outage_client, method, path, body):
    """All critical routes must return 503 when the DB is unavailable."""
    from httpx import ASGITransport, AsyncClient

    from app.database import get_db
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_db] = _make_broken_db()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        if method == "GET":
            resp = await ac.get(path, headers=_BEARER)
        else:
            resp = await ac.request(method, path, json=body, headers=_BEARER)

    assert resp.status_code == 503, (
        f"{method} {path} → expected 503, got {resp.status_code}; body={resp.text}"
    )


@pytest.mark.parametrize("method,path,body", _503_ROUTES)
async def test_503_response_is_structured_json(method, path, body):
    """503 response must be valid JSON with the required fields — no tracebacks."""
    from httpx import ASGITransport, AsyncClient

    from app.database import get_db
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_db] = _make_broken_db()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        if method == "GET":
            resp = await ac.get(path, headers=_BEARER)
        else:
            resp = await ac.request(method, path, json=body, headers=_BEARER)

    assert resp.status_code == 503

    # Must be valid JSON
    data = resp.json()

    # No raw traceback leaked in the response body
    body_text = resp.text
    assert "Traceback" not in body_text
    assert "sqlalchemy" not in body_text.lower() or "database_unavailable" in body_text

    # Must carry a human-readable message
    # The 503 can come either from get_db (HTTPException detail dict) or
    # from the global SQLAlchemy exception handler (flat dict).
    detail = data.get("detail") or data
    if isinstance(detail, dict):
        assert "message" in detail, f"Expected 'message' in detail: {detail}"
        assert detail.get("error") == "database_unavailable"
    else:
        # Fallback: at minimum the top-level response must have a message
        assert "message" in data or "detail" in data


@pytest.mark.parametrize("method,path,body", _503_ROUTES)
async def test_503_content_type_is_json(method, path, body):
    """503 response must have Content-Type: application/json."""
    from httpx import ASGITransport, AsyncClient

    from app.database import get_db
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_db] = _make_broken_db()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        if method == "GET":
            resp = await ac.get(path, headers=_BEARER)
        else:
            resp = await ac.request(method, path, json=body, headers=_BEARER)

    assert resp.status_code == 503
    assert "application/json" in resp.headers.get("content-type", "")


# ── disconnection / timeout variants ─────────────────────────────────────────

async def test_disconnection_error_returns_503():
    """DisconnectionError must also map to 503."""
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy.exc import DisconnectionError

    from app.database import get_db
    from app.main import create_app

    async def broken_disconnection():
        raise DisconnectionError()
        yield  # noqa: unreachable

    app = create_app()
    app.dependency_overrides[get_db] = broken_disconnection

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/dashboard", headers=_BEARER)

    assert resp.status_code == 503
    data = resp.json()
    assert "message" in (data.get("detail") or data)


async def test_timeout_error_returns_503():
    """SQLAlchemy TimeoutError must map to 503."""
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy.exc import TimeoutError as SATimeoutError

    from app.database import get_db
    from app.main import create_app

    async def broken_timeout():
        raise SATimeoutError()
        yield  # noqa: unreachable

    app = create_app()
    app.dependency_overrides[get_db] = broken_timeout

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/api/v1/journey", headers=_BEARER)

    assert resp.status_code == 503
    data = resp.json()
    assert "message" in (data.get("detail") or data)


# ── normal requests still work ────────────────────────────────────────────────

async def test_health_unaffected_by_db_override(client):
    """GET /health must return 200 regardless of DB state (it does not use DB)."""
    resp = await client.get("/health")
    assert resp.status_code == 200
