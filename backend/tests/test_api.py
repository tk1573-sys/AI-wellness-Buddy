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
    resp = await client.get("/api/v1/auth/me", params={"token": token})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "me@example.com"
    assert data["username"] == "meuser"


async def test_me_invalid_token_returns_401(client):
    resp = await client.get("/api/v1/auth/me", params={"token": "not-a-valid-token"})
    assert resp.status_code == 401


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
        params={"token": "bad-token"},
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
        params={"token": token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert data["primary_emotion"] == "sadness"
    assert "session_id" in data


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
        params={"token": token},
    )

    resp = await client.get("/api/v1/chat/history", params={"token": token})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
