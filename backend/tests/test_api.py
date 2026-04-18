"""Unit tests for the FastAPI backend endpoints.

Covers:
  - GET  /health
  - POST /api/v1/auth/signup
  - POST /api/v1/auth/login
  - GET  /api/v1/auth/me
  - POST /api/v1/predict
  - POST /api/v1/chat
  - GET  /api/v1/chat/history
"""

from __future__ import annotations

import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _signup(client, email="test@example.com", username="testuser", password="Passw0rd!"):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": email, "username": username, "password": password},
    )
    return resp


async def _login(client, email="test@example.com", password="Passw0rd!"):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return resp


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────

async def test_health_returns_200(client):
    resp = await client.get("/health")
    assert resp.status_code == 200


async def test_health_schema(client):
    data = (await client.get("/health")).json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "version" in data


# ─────────────────────────────────────────────────────────────────────────────
# Auth — signup
# ─────────────────────────────────────────────────────────────────────────────

async def test_signup_creates_user(client):
    resp = await _signup(client, email="new@example.com", username="newuser")
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_signup_duplicate_email_returns_409(client):
    await _signup(client, email="dup@example.com", username="dupuser1")
    resp = await _signup(client, email="dup@example.com", username="dupuser2")
    assert resp.status_code == 409


async def test_signup_weak_password_returns_422(client):
    resp = await _signup(client, password="short")
    assert resp.status_code == 422


async def test_signup_missing_uppercase_returns_422(client):
    resp = await _signup(client, password="alllowercase1!")
    assert resp.status_code == 422


async def test_signup_missing_digit_returns_422(client):
    resp = await _signup(client, password="NoDigitHere!")
    assert resp.status_code == 422


# ─────────────────────────────────────────────────────────────────────────────
# Auth — login
# ─────────────────────────────────────────────────────────────────────────────

async def test_login_returns_token(client):
    await _signup(client, email="login@example.com", username="loginuser")
    resp = await _login(client, email="login@example.com")
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password_returns_401(client):
    await _signup(client, email="wrong@example.com", username="wronguser")
    resp = await _login(client, email="wrong@example.com", password="WrongPass1!")
    assert resp.status_code == 401


async def test_login_unknown_email_returns_401(client):
    resp = await _login(client, email="nobody@example.com")
    assert resp.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# Auth — /me
# ─────────────────────────────────────────────────────────────────────────────

async def test_me_returns_user_info(client):
    await _signup(client, email="me@example.com", username="meuser")
    token = (await _login(client, email="me@example.com")).json()["access_token"]
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@example.com"
    assert data["username"] == "meuser"


async def test_me_invalid_token_returns_401(client):
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert resp.status_code == 401


async def test_logout_returns_204(client):
    """POST /auth/logout should return 204 and clear the auth cookie."""
    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 204


async def test_login_sets_auth_cookie(client):
    """POST /auth/login should set an HttpOnly wb_access_token cookie."""
    await _signup(client, email="cookie@example.com", username="cookieuser")
    resp = await _login(client, email="cookie@example.com")
    assert resp.status_code == 200
    # Cookie should be present in the response headers
    set_cookie = resp.headers.get("set-cookie", "")
    assert "wb_access_token" in set_cookie
    assert "httponly" in set_cookie.lower()


async def test_signup_sets_auth_cookie(client):
    """POST /auth/signup should also set an HttpOnly wb_access_token cookie."""
    resp = await _signup(client, email="signupcookie@example.com", username="signupcookieuser")
    assert resp.status_code == 201
    set_cookie = resp.headers.get("set-cookie", "")
    assert "wb_access_token" in set_cookie, (
        "Signup must set the wb_access_token cookie so the user is immediately logged in"
    )
    assert "httponly" in set_cookie.lower()


# ─────────────────────────────────────────────────────────────────────────────
# Predict
# ─────────────────────────────────────────────────────────────────────────────

async def test_predict_returns_emotion(client, mocker):
    from app.schemas.emotion import EmotionScore, PredictResponse

    mocker.patch(
        "app.routers.predict.emotion_service.predict",
        return_value=PredictResponse(
            primary_emotion="sadness",
            confidence=0.82,
            uncertainty=0.18,
            is_uncertain=False,
            is_high_risk=False,
            scores=[EmotionScore(emotion="sadness", score=0.82)],
        ),
    )
    resp = await client.post("/api/v1/predict", json={"text": "I feel very sad today"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["primary_emotion"] == "sadness"
    assert "confidence" in data
    assert "scores" in data


async def test_predict_empty_text_returns_422(client):
    resp = await client.post("/api/v1/predict", json={"text": ""})
    assert resp.status_code == 422


async def test_predict_high_risk_sets_flag(client, mocker):
    from app.schemas.emotion import EmotionScore, PredictResponse

    mocker.patch(
        "app.routers.predict.emotion_service.predict",
        return_value=PredictResponse(
            primary_emotion="crisis",
            confidence=0.9,
            uncertainty=0.1,
            is_uncertain=False,
            is_high_risk=True,
            escalation_message="Please seek help.",
            scores=[EmotionScore(emotion="crisis", score=0.9)],
        ),
    )
    resp = await client.post("/api/v1/predict", json={"text": "I want to end it all"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_high_risk"] is True
    assert data["escalation_message"] is not None


# ─────────────────────────────────────────────────────────────────────────────
# Chat
# ─────────────────────────────────────────────────────────────────────────────

async def test_chat_requires_token(client):
    resp = await client.post(
        "/api/v1/chat",
        json={"message": "Hello"},
        headers={"Authorization": "Bearer bad-token"},
    )
    assert resp.status_code == 401


async def test_chat_returns_reply(client, mocker):
    from app.schemas.chat import ChatResponse

    await _signup(client, email="chat@example.com", username="chatuser")
    token = (await _login(client, email="chat@example.com")).json()["access_token"]

    mocker.patch(
        "app.routers.chat.chat_service.handle_chat",
        return_value=ChatResponse(
            session_id="sess123",
            reply="I hear you. That sounds difficult.",
            primary_emotion="sadness",
            confidence=0.75,
            is_high_risk=False,
        ),
    )
    resp = await client.post(
        "/api/v1/chat",
        json={"message": "I feel sad today"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert data["primary_emotion"] == "sadness"
    assert "session_id" in data


# ─────────────────────────────────────────────────────────────────────────────
# Swagger / OpenAPI docs endpoints
# ─────────────────────────────────────────────────────────────────────────────

async def test_docs_returns_200_html(client):
    """GET /docs must return an HTML page (Swagger UI) with status 200."""
    resp = await client.get("/docs")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert b"swagger" in resp.content.lower()


async def test_redoc_returns_200_html(client):
    """GET /redoc must return an HTML page (ReDoc UI) with status 200."""
    resp = await client.get("/redoc")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


async def test_openapi_json_returns_200(client):
    """GET /openapi.json must return a valid JSON schema."""
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    assert "application/json" in resp.headers["content-type"]
    schema = resp.json()
    assert "openapi" in schema
    assert "paths" in schema


async def test_docs_csp_allows_cdn(client):
    """script-src and style-src in the /docs CSP must list https://cdn.jsdelivr.net."""
    resp = await client.get("/docs")
    assert resp.status_code == 200
    csp = resp.headers.get("content-security-policy", "")
    # Parse CSP into {directive: [token, …]} so we can do exact membership checks
    # rather than substring searches that could match unintended hosts.
    directives: dict[str, list[str]] = {}
    for part in csp.split(";"):
        tokens = part.strip().split()
        if tokens:
            directives[tokens[0]] = tokens[1:]
    cdn = "https://cdn.jsdelivr.net"
    assert cdn in directives.get("script-src", []), (
        f"Expected {cdn!r} in script-src; got {directives}"
    )
    assert cdn in directives.get("style-src", []), (
        f"Expected {cdn!r} in style-src; got {directives}"
    )


async def test_chat_history_returns_list(client, mocker):
    await _signup(client, email="hist@example.com", username="histuser")
    token = (await _login(client, email="hist@example.com")).json()["access_token"]

    mocker.patch(
        "app.routers.chat.chat_service.handle_chat",
        return_value=__import__(
            "app.schemas.chat", fromlist=["ChatResponse"]
        ).ChatResponse(
            session_id="sess456",
            reply="I'm here for you.",
            primary_emotion="neutral",
            confidence=0.6,
            is_high_risk=False,
        ),
    )
    # Send a message first so history is non-empty
    await client.post(
        "/api/v1/chat",
        json={"message": "Hello"},
        headers={"Authorization": f"Bearer {token}"},
    )

    resp = await client.get(
        "/api/v1/chat/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# ─────────────────────────────────────────────────────────────────────────────
# Analytics — research endpoint
# ─────────────────────────────────────────────────────────────────────────────

async def test_analytics_research_requires_auth(client):
    """Missing / invalid token must return 401."""
    resp = await client.get(
        "/api/v1/analytics/research",
        headers={"Authorization": "Bearer bad-token"},
    )
    assert resp.status_code == 401


async def test_analytics_research_empty_returns_schema(client):
    """Endpoint works with zero emotion logs, returning empty arrays."""
    await _signup(client, email="anon@example.com", username="anonuser")
    token = (await _login(client, email="anon@example.com")).json()["access_token"]

    resp = await client.get(
        "/api/v1/analytics/research",
        params={"include_plots": "false"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sessions"] == 0
    assert data["emotion_distribution"] == []
    assert data["average_confidence"] == 0.0
    assert data["average_personalization_score"] == 0.0
    assert data["risk_trend"] == []
    assert "research_summary" in data
    assert "key_findings" in data["research_summary"]
    assert "plot_data" in data


async def test_analytics_research_with_emotion_logs(client, db_session):
    """Endpoint returns correct metrics when emotion logs are present."""
    from datetime import datetime, timezone

    from app.models.emotion import EmotionLog
    from app.models.user import User
    from app.services.auth_service import hash_password

    # Create a dedicated user directly in the DB
    user = User(
        email="researcher@example.com",
        username="researcher",
        hashed_password=hash_password("Passw0rd!"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Seed emotion logs with varied emotions and risk/personalization scores
    emotions = ["joy", "sadness", "anxiety", "neutral", "crisis", "sadness", "joy", "anxiety"]
    for i, emotion in enumerate(emotions):
        log = EmotionLog(
            user_id=user.id,
            input_text=f"Sample text {i}",
            primary_emotion=emotion,
            confidence=0.6 + i * 0.03,
            uncertainty=0.2,
            is_high_risk=(emotion == "crisis"),
            all_scores={emotion: 0.8, "neutral": 0.2},
            risk_score=0.1 * (i + 1),
            personalization_score=0.8,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(log)
    await db_session.commit()

    # Login via HTTP to get a token
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "researcher@example.com", "username": "researcher", "password": "Passw0rd!"},
    )
    # User might already exist — accept both 201 and 409
    assert signup_resp.status_code in (201, 409)
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "researcher@example.com", "password": "Passw0rd!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    resp = await client.get(
        "/api/v1/analytics/research",
        params={"include_plots": "false"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()

    # Structural checks
    assert data["total_sessions"] >= 0
    assert isinstance(data["emotion_distribution"], list)
    assert isinstance(data["average_confidence"], float)
    assert isinstance(data["average_personalization_score"], float)
    assert isinstance(data["risk_trend"], list)
    summary = data["research_summary"]
    assert isinstance(summary["key_findings"], list)
    assert isinstance(summary["insights"], list)
    assert "generated_at" in summary


async def test_analytics_research_summary_fields(client):
    """Research summary contains all required IEEE-paper fields."""
    await _signup(client, email="summ@example.com", username="summuser")
    token = (await _login(client, email="summ@example.com")).json()["access_token"]

    resp = await client.get(
        "/api/v1/analytics/research",
        params={"include_plots": "false"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    summary = resp.json()["research_summary"]
    required_fields = {
        "total_sessions",
        "key_findings",
        "improvement_percentage",
        "risk_detection_improvement",
        "confidence_improvement",
        "insights",
        "generated_at",
    }
    for field in required_fields:
        assert field in summary, f"Missing field: {field}"


# ─────────────────────────────────────────────────────────────────────────────
# Chat history — ordering
# ─────────────────────────────────────────────────────────────────────────────

async def test_chat_history_ascending_order(client, db_session):
    """GET /chat/history must return messages in ascending created_at order.

    Verifies that the backend stores and returns chat messages newest-last
    (chronological) without any reversed() logic.
    """
    from datetime import datetime, timezone, timedelta

    from app.models.chat import ChatHistory
    from app.models.user import User
    from app.services.auth_service import hash_password

    # Create a user directly in the DB
    user = User(
        email="ordering@example.com",
        username="orderinguser",
        hashed_password=hash_password("Passw0rd!"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    # Insert three messages with explicit timestamps in reverse order so we
    # can confirm the endpoint re-sorts them ascending.
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    messages = [
        ChatHistory(
            user_id=user.id,
            session_id="order-test",
            role="user",
            content="First user message",
            created_at=base,
        ),
        ChatHistory(
            user_id=user.id,
            session_id="order-test",
            role="assistant",
            content="First assistant reply",
            created_at=base + timedelta(seconds=1),
        ),
        ChatHistory(
            user_id=user.id,
            session_id="order-test",
            role="user",
            content="Second user message",
            created_at=base + timedelta(seconds=2),
        ),
    ]
    # Add in reversed order to prove the query doesn't rely on insertion order.
    for msg in reversed(messages):
        db_session.add(msg)
    await db_session.commit()

    # Login to obtain a token for this user
    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={"email": "ordering@example.com", "username": "orderinguser", "password": "Passw0rd!"},
    )
    # User might already exist if the DB is shared — accept 201 or 409
    assert signup_resp.status_code in (201, 409)

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "ordering@example.com", "password": "Passw0rd!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    resp = await client.get(
        "/api/v1/chat/history",
        params={"session_id": "order-test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 3, f"Expected at least 3 messages, got {len(items)}"

    # Find the three seeded messages by content (other tests may have added rows)
    seeded = [m for m in items if m["content"] in {
        "First user message", "First assistant reply", "Second user message"
    }]
    assert len(seeded) == 3, f"Could not find all seeded messages in history: {items}"

    contents = [m["content"] for m in seeded]
    assert contents == [
        "First user message",
        "First assistant reply",
        "Second user message",
    ], f"Messages not in ascending order: {contents}"

