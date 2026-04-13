"""Insights router — AI-generated summary for the authenticated user.

Endpoint:
    GET /api/v1/insights
        Returns dominant emotion, personalization score, trigger signals,
        risk level, recent emotion pattern, and mood trend derived from
        the user's emotion logs and profile.

Always returns HTTP 200 with a safe fallback when no data exists.
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.emotion import EmotionLog
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/insights", tags=["Insights"])

_INSIGHTS_LOG_LIMIT = 30
_NEGATIVE = frozenset({"sadness", "anger", "fear", "anxiety", "crisis", "stress"})
_RISK_EMOTIONS = frozenset({"crisis", "anger", "fear"})


# --------------------------------------------------------------------------- #
# Response schema
# --------------------------------------------------------------------------- #

class InsightsResponse(BaseModel):
    dominant_emotion: str
    personalization_score: float
    trigger_signals: list[str]
    risk_level: str          # "low" | "moderate" | "high" | "critical"
    recent_pattern: dict[str, float]
    trend: str               # "improving" | "stable" | "declining"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

_EMPTY_RESPONSE = InsightsResponse(
    dominant_emotion="neutral",
    personalization_score=0.0,
    trigger_signals=[],
    risk_level="low",
    recent_pattern={},
    trend="stable",
)


def _compute_risk_level(logs: list[EmotionLog]) -> str:
    if not logs:
        return "low"
    crisis_count = sum(1 for l in logs if l.primary_emotion == "crisis")
    high_risk_count = sum(1 for l in logs if l.is_high_risk)
    avg_risk = sum(l.risk_score for l in logs) / len(logs)

    if crisis_count >= 2 or avg_risk >= 0.75:
        return "critical"
    if crisis_count >= 1 or high_risk_count >= 2 or avg_risk >= 0.5:
        return "high"
    if high_risk_count >= 1 or avg_risk >= 0.25:
        return "moderate"
    return "low"


def _compute_trend(emotions: list[str]) -> str:
    if len(emotions) < 4:
        return "stable"
    mid = len(emotions) // 2
    earlier_neg = sum(1 for e in emotions[:mid] if e in _NEGATIVE)
    recent_neg = sum(1 for e in emotions[mid:] if e in _NEGATIVE)
    if recent_neg < earlier_neg:
        return "improving"
    if recent_neg > earlier_neg:
        return "declining"
    return "stable"


def _extract_trigger_signals(logs: list[EmotionLog], profile_triggers: dict | None) -> list[str]:
    """Derive trigger signals from profile trigger flags and high-risk logs."""
    signals: list[str] = []

    # Signals from profile's active triggers
    if profile_triggers:
        signals.extend(k for k, v in profile_triggers.items() if v)

    # Add dominant negative emotion as a signal when it appears repeatedly
    if logs:
        counter = Counter(l.primary_emotion for l in logs if l.primary_emotion in _NEGATIVE)
        if counter:
            top_neg, top_count = counter.most_common(1)[0]
            if top_count >= 2 and top_neg not in signals:
                signals.append(top_neg)

    # Deduplicate while preserving order, cap at 5
    seen: set[str] = set()
    unique: list[str] = []
    for s in signals:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique[:5]


# --------------------------------------------------------------------------- #
# Endpoint
# --------------------------------------------------------------------------- #

@router.get("", response_model=InsightsResponse)
async def get_insights(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> InsightsResponse:
    """Return AI insight summary for the authenticated user.

    Derived from the most recent emotion logs and the stored profile.
    Always returns HTTP 200; an empty fallback is returned when no data exists.
    """
    try:
        stmt = (
            select(EmotionLog)
            .where(EmotionLog.user_id == user.id)
            .order_by(EmotionLog.created_at.desc())
            .limit(_INSIGHTS_LOG_LIMIT)
        )
        result = await db.execute(stmt)
        logs: list[EmotionLog] = list(result.scalars().all())

        if not logs:
            return _EMPTY_RESPONSE

        # Dominant emotion
        emotion_counter = Counter(l.primary_emotion for l in logs)
        dominant_emotion = emotion_counter.most_common(1)[0][0]

        # Average personalization score
        avg_personalization = round(
            sum(l.personalization_score for l in logs) / len(logs), 4
        )

        # Recent pattern — percentage distribution across all emotion labels
        total = len(logs)
        recent_pattern = {
            emotion: round(count / total * 100, 1)
            for emotion, count in sorted(
                emotion_counter.items(), key=lambda x: x[1], reverse=True
            )
        }

        # Trend
        emotion_list = [l.primary_emotion for l in reversed(logs)]  # oldest first
        trend = _compute_trend(emotion_list)

        # Risk level
        risk_level = _compute_risk_level(logs)

        # Trigger signals — load profile for active trigger flags
        profile_triggers: dict | None = None
        try:
            from app.models.profile import UserProfile  # noqa: PLC0415
            prof_result = await db.execute(
                select(UserProfile).where(UserProfile.user_id == user.id)
            )
            profile = prof_result.scalar_one_or_none()
            if profile is not None:
                profile_triggers = profile.triggers
        except Exception:  # noqa: BLE001
            logger.debug(
            "Could not load profile for trigger signals user_id=%d",
            user.id,
            exc_info=True,
        )

        trigger_signals = _extract_trigger_signals(logs, profile_triggers)

        logger.info(
            "insights user_id=%d logs=%d dominant=%s risk=%s trend=%s",
            user.id, len(logs), dominant_emotion, risk_level, trend,
        )

        return InsightsResponse(
            dominant_emotion=dominant_emotion,
            personalization_score=avg_personalization,
            trigger_signals=trigger_signals,
            risk_level=risk_level,
            recent_pattern=recent_pattern,
            trend=trend,
        )

    except Exception:  # noqa: BLE001
        logger.exception("insights endpoint error for user_id=%d — returning fallback", user.id)
        return _EMPTY_RESPONSE
