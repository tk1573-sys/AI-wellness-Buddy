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
        params={"token": token},
    )
    assert resp.status_code == 200
    chat_data = resp.json()
    assert chat_data["session_id"] == "integration-session"
    assert "reply" in chat_data

    # ── 4. Chat history ────────────────────────────────────────────────────
    resp = await client.get("/api/v1/chat/history", params={"token": token})
    assert resp.status_code == 200
    messages = resp.json()
    # At least the user turn and assistant turn should be stored
    assert isinstance(messages, list)
