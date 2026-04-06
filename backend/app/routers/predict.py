"""Emotion prediction router."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.limiter import limiter
from app.models.emotion import EmotionLog
from app.routers.auth import get_optional_user
from app.schemas.emotion import PredictRequest, PredictResponse
from app.services import emotion_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Predict"])
settings = get_settings()

# Weights for computing a composite risk_score from emotion probability distributions.
# Crisis is weighted at 1.0 (fully high-risk); fear/anxiety/sadness/anger contribute less.
_RISK_WEIGHTS: dict[str, float] = {
    "crisis": 1.0,
    "fear": 0.6,
    "anxiety": 0.5,
    "sadness": 0.3,
    "anger": 0.3,
}


@router.post("", response_model=PredictResponse)
@limiter.limit(settings.RATE_LIMIT_PREDICT)
async def predict(
    request: Request,
    req: PredictRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_optional_user),
):
    """
    Detect emotion in a piece of text using the hybrid AI model.

    - Returns the primary emotion, confidence score, and full distribution.
    - Flags high-risk inputs and returns an escalation message when appropriate.
    - Prediction is persisted for authenticated users (pass Authorization: Bearer header).
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
    if user is not None:
        try:
            all_scores_dict = {s.emotion: s.score for s in result.scores}
            # risk_score: weighted sum of high-risk emotion probabilities, capped at 1.0
            risk_score = min(
                1.0,
                sum(all_scores_dict.get(e, 0.0) * w for e, w in _RISK_WEIGHTS.items()),
            )
            # personalization_score: inverse of uncertainty (higher certainty = more personalized)
            personalization_score = round(1.0 - result.uncertainty, 4)
            db.add(EmotionLog(
                user_id=user.id,
                input_text=req.text,
                primary_emotion=result.primary_emotion,
                confidence=result.confidence,
                uncertainty=result.uncertainty,
                is_high_risk=result.is_high_risk,
                all_scores=all_scores_dict,
                risk_score=round(risk_score, 4),
                personalization_score=personalization_score,
            ))
        except Exception:
            # Persistence failure must not block the prediction response.
            logger.warning("Could not persist emotion log (DB error)")

    return result

