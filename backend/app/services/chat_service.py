"""Chat service: maintains conversation context and persists history."""

from __future__ import annotations

import logging
import secrets
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatHistory
from app.models.emotion import EmotionLog
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.emotion_service import predict

# Allow importing the AI modules in the project root.
_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

logger = logging.getLogger(__name__)

# Per-process pipeline registry (same isolation strategy as the original
# api_service.py, but now keyed by database user_id instead of arbitrary str).
_pipelines: dict[int, object] = {}


def _get_pipeline(user_id: int):
    """Lazily initialise a WellnessAgentPipeline for the given user."""
    if user_id not in _pipelines:
        from agent_pipeline import WellnessAgentPipeline  # noqa: PLC0415
        _pipelines[user_id] = WellnessAgentPipeline()
    return _pipelines[user_id]


async def handle_chat(
    db: AsyncSession,
    user_id: int,
    req: ChatRequest,
) -> ChatResponse:
    """Process one chat turn, persist to DB, and return structured reply."""

    session_id = req.session_id or secrets.token_hex(16)
    pipeline = _get_pipeline(user_id)

    # Run full agent pipeline (emotion → pattern → response)
    try:
        result = pipeline.process_turn(req.message, context={"user_name": str(user_id)})
    except Exception:
        logger.exception("Pipeline error for user_id=%d", user_id)
        result = {
            "response": "I'm here for you. Could you tell me more about how you're feeling?",
            "emotion": {"primary_emotion": "neutral", "confidence_score": 0.5},
            "patterns": {},
        }

    emotion_data: dict = result.get("emotion") or {}
    primary = emotion_data.get("primary_emotion", "neutral")
    confidence = float(emotion_data.get("confidence_score", 0.5))
    reply_text: str = result.get("response", "")
    patterns: dict = result.get("patterns") or {}

    # Safety gate
    crisis_score = (emotion_data.get("final_probabilities") or {}).get("crisis", 0.0)
    from app.config import get_settings
    settings = get_settings()
    is_high_risk = (
        primary == "crisis"
        or float(crisis_score) >= settings.CRISIS_CONFIDENCE_THRESHOLD
    )
    escalation_message = settings.HIGH_RISK_ESCALATION_MESSAGE if is_high_risk else None

    # Build score list for the response
    raw_scores: dict = (
        emotion_data.get("final_probabilities")
        or emotion_data.get("confidence_distribution")
        or {}
    )
    scores = [
        {"emotion": e, "score": round(s, 4)}
        for e, s in sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    # Persist user message
    db.add(ChatHistory(
        user_id=user_id,
        session_id=session_id,
        role="user",
        content=req.message,
        emotion=primary,
    ))

    # Persist assistant reply
    db.add(ChatHistory(
        user_id=user_id,
        session_id=session_id,
        role="assistant",
        content=reply_text,
    ))

    # Persist emotion log
    db.add(EmotionLog(
        user_id=user_id,
        input_text=req.message,
        primary_emotion=primary,
        confidence=round(confidence, 4),
        uncertainty=round(float(emotion_data.get("uncertainty_score", 0.5)), 4),
        is_high_risk=is_high_risk,
        all_scores=raw_scores,
    ))

    logger.info(
        "chat user_id=%d session=%s emotion=%s is_high_risk=%s",
        user_id, session_id, primary, is_high_risk,
    )

    return ChatResponse(
        session_id=session_id,
        reply=reply_text,
        primary_emotion=primary,
        confidence=round(confidence, 4),
        is_high_risk=is_high_risk,
        escalation_message=escalation_message,
        scores=scores,
    )
