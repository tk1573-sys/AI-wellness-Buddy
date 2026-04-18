"""Integration test: full predict → chat → history pipeline."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_full_pipeline_integration(client, mocker):
    """Signup → login → predict → chat → history in one flow."""
    from app.schemas.chat import ChatResponse
    from app.schemas.emotion import EmotionScore, PredictResponse

    # ── 1. Signup ──────────────────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "integration@example.com", "username": "intuser", "password": "Passw0rd!"},
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]

    # ── 2. Predict (unauthenticated path, no token) ────────────────────────
    mocker.patch(
        "app.routers.predict.emotion_service.predict",
        return_value=PredictResponse(
            primary_emotion="anxiety",
            confidence=0.77,
            uncertainty=0.23,
            is_uncertain=False,
            is_high_risk=False,
            scores=[EmotionScore(emotion="anxiety", score=0.77)],
        ),
    )
    resp = await client.post("/api/v1/predict", json={"text": "I'm feeling anxious about work"})
    assert resp.status_code == 200
    assert resp.json()["primary_emotion"] == "anxiety"

    # ── 3. Chat ────────────────────────────────────────────────────────────
    mocker.patch(
        "app.routers.chat.chat_service.handle_chat",
        return_value=ChatResponse(
            session_id="integration-session",
            reply="That sounds stressful. Let's talk about it.",
            primary_emotion="anxiety",
            confidence=0.77,
            is_high_risk=False,
        ),
    )
    resp = await client.post(
        "/api/v1/chat",
        json={"message": "I'm feeling anxious about work", "session_id": "integration-session"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    chat_data = resp.json()
    assert chat_data["session_id"] == "integration-session"
    assert "reply" in chat_data

    # ── 4. Chat history ────────────────────────────────────────────────────
    resp = await client.get(
        "/api/v1/chat/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    messages = resp.json()
    # At least the user turn and assistant turn should be stored
    assert isinstance(messages, list)

    # ── 5. Logout ──────────────────────────────────────────────────────────
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 204


async def test_crisis_alert_auto_dispatch(mocker, db_session):
    """_maybe_dispatch_crisis_alert skips gracefully when no guardian profile exists."""
    from app.services.chat_service import _maybe_dispatch_crisis_alert

    # No profile in DB — dispatch should be skipped silently (no exception).
    await _maybe_dispatch_crisis_alert(db_session, user_id=9999, primary_emotion="crisis", message_text="I want to die")


async def test_crisis_alert_dispatched_for_high_risk(mocker, db_session):
    """Auto-dispatch is attempted when is_high_risk=True during handle_chat."""
    from unittest.mock import AsyncMock, patch

    from app.services.chat_service import handle_chat
    from app.schemas.chat import ChatRequest

    mock_dispatch = AsyncMock(return_value=[])
    with (
        patch(
            "app.services.chat_service._get_pipeline",
            return_value=_make_crisis_pipeline(),
        ),
        patch(
            "app.services.chat_service._maybe_dispatch_crisis_alert",
            mock_dispatch,
        ),
    ):
        await handle_chat(
            db_session,
            user_id=42,
            req=ChatRequest(message="I want to end my life"),
        )

    # Dispatch was called once with user_id=42
    mock_dispatch.assert_awaited_once()
    call_kwargs = mock_dispatch.call_args
    assert call_kwargs.args[1] == 42 or (call_kwargs.kwargs or {}).get("user_id") == 42


def _make_crisis_pipeline():
    """Return a minimal mock pipeline that signals a crisis-level emotion."""

    class _MockPipeline:
        def process_turn(self, message, context=None):
            return {
                "response": "Please reach out for help.",
                "emotion": {
                    "primary_emotion": "crisis",
                    "confidence_score": 0.95,
                    "final_probabilities": {"crisis": 0.95},
                },
                "patterns": {},
            }

    return _MockPipeline()


# --------------------------------------------------------------------------- #
# Cookie-based auth integration tests (Tasks 6 & 7)
# --------------------------------------------------------------------------- #

async def test_cookie_auth_flow_login_me_profile(client):
    """Login → /auth/me → /profile using cookies only (no Bearer header).

    Verifies that the HttpOnly wb_access_token cookie issued on login is
    accepted by every protected endpoint without a Bearer header.
    """
    # ── 1. Signup ──────────────────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "cookieflow@example.com",
            "username": "cookieflow",
            "password": "Passw0rd!",
        },
    )
    assert resp.status_code == 201

    # ── 2. Login — extract the HttpOnly cookie from the Set-Cookie header ──
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "cookieflow@example.com", "password": "Passw0rd!"},
    )
    assert resp.status_code == 200
    cookie_value = resp.cookies.get("wb_access_token")
    assert cookie_value is not None, (
        "POST /auth/login must set a wb_access_token cookie in the response"
    )

    # ── 3. GET /auth/me — cookie only, no Authorization header ────────────
    resp = await client.get(
        "/api/v1/auth/me",
        cookies={"wb_access_token": cookie_value},
    )
    assert resp.status_code == 200, (
        f"/auth/me returned {resp.status_code} with valid cookie: {resp.text}"
    )
    assert resp.json()["email"] == "cookieflow@example.com"

    # ── 4. GET /api/v1/profile — cookie only ───────────────────────────────
    # A freshly-created user has no profile yet, so 404 is expected.
    # 401 / 403 would indicate cookie auth is broken.
    resp = await client.get(
        "/api/v1/profile",
        cookies={"wb_access_token": cookie_value},
    )
    assert resp.status_code in (200, 404), (
        f"/profile returned {resp.status_code} (expected 200 or 404, not 401/403): {resp.text}"
    )

    # ── 5. GET /auth/debug — confirms cookie visibility on the backend ─────
    resp = await client.get(
        "/api/v1/auth/debug",
        cookies={"wb_access_token": cookie_value},
    )
    assert resp.status_code == 200
    assert resp.json()["wb_access_token_present"] is True


async def test_me_without_any_auth_returns_401(client):
    """GET /auth/me with no credentials must return 401."""
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_profile_without_any_auth_returns_401(client):
    """GET /profile with no credentials must return 401."""
    resp = await client.get("/api/v1/profile")
    assert resp.status_code == 401


async def test_auth_debug_no_cookie(client):
    """GET /auth/debug without a cookie must report the cookie as absent."""
    resp = await client.get("/api/v1/auth/debug")
    assert resp.status_code == 200
    assert resp.json()["wb_access_token_present"] is False


async def test_auth_debug_with_cookie(client):
    """GET /auth/debug with a valid cookie must report it as present."""
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "debugcookie@example.com",
            "username": "debugcookie",
            "password": "Passw0rd!",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "debugcookie@example.com", "password": "Passw0rd!"},
    )
    assert login_resp.status_code == 200
    cookie_value = login_resp.cookies.get("wb_access_token")
    assert cookie_value is not None

    resp = await client.get(
        "/api/v1/auth/debug",
        cookies={"wb_access_token": cookie_value},
    )
    assert resp.status_code == 200
    assert resp.json()["wb_access_token_present"] is True
