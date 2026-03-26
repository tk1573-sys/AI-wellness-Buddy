"""Emotion prediction router."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.emotion import EmotionLog
from app.routers.auth import get_current_user
from app.schemas.emotion import PredictRequest, PredictResponse
from app.services import emotion_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Predict"])


@router.post("", response_model=PredictResponse)
async def predict(
    req: PredictRequest,
    token: str = "",
    db: AsyncSession = Depends(get_db),
):
    """
    Detect emotion in a piece of text using the hybrid AI model.

    - Returns the primary emotion, confidence score, and full distribution.
    - Flags high-risk inputs and returns an escalation message when appropriate.
    - Prediction is persisted for authenticated users (pass `token` query param).
    """
    t0 = time.perf_counter()
    try:
        result = emotion_service.predict(req.text)
    except Exception as exc:
        logger.exception("Prediction failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Emotion prediction failed. Please try again.",
        ) from exc

    latency_ms = round((time.perf_counter() - t0) * 1000, 1)
    logger.info("predict latency_ms=%.1f emotion=%s", latency_ms, result.primary_emotion)

    # Persist if the caller is authenticated
    if token:
        try:
            user = await get_current_user(token, db)
            db.add(EmotionLog(
                user_id=user.id,
                input_text=req.text,
                primary_emotion=result.primary_emotion,
                confidence=result.confidence,
                uncertainty=result.uncertainty,
                is_high_risk=result.is_high_risk,
                all_scores={s.emotion: s.score for s in result.scores},
            ))
        except Exception:
            # Persistence failure must not block the prediction response.
            logger.warning("Could not persist emotion log (unauthenticated or DB error)")

    return result
