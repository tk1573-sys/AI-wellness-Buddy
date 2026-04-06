"""Dashboard router — emotion analytics and risk summary."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.emotion import EmotionLog
from app.routers.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

EMOTION_MEMORY_LIMIT = 20


class EmotionPoint(BaseModel):
    timestamp: str
    emotion: str
    confidence: float
    is_high_risk: bool


class TriggerFrequency(BaseModel):
    emotion: str
    count: int


class RiskAlert(BaseModel):
    level: str   # "high" | "critical"
    message: str
    timestamp: str


class DashboardResponse(BaseModel):
    emotion_trend: list[EmotionPoint]
    emotion_distribution: list[TriggerFrequency]
    risk_alerts: list[RiskAlert]
    mood_trend: str      # "improving" | "stable" | "declining"
    escalation_detected: bool
    total_sessions: int


def _detect_mood_trend(emotions: list[str]) -> str:
    """Return a simple mood trend based on the last 10 emotions."""
    NEGATIVE = {"sadness", "anger", "fear", "anxiety", "crisis", "stress"}
    POSITIVE = {"joy", "neutral"}

    if len(emotions) < 3:
        return "stable"

    recent = emotions[-5:]
    earlier = emotions[:-5] if len(emotions) > 5 else emotions[:len(emotions) // 2]

    recent_neg = sum(1 for e in recent if e in NEGATIVE)
    earlier_neg = sum(1 for e in earlier if e in NEGATIVE)

    if recent_neg < earlier_neg:
        return "improving"
    elif recent_neg > earlier_neg:
        return "declining"
    return "stable"


def _detect_escalation(emotions: list[str]) -> bool:
    """True if escalation pathway found or 3+ consecutive negatives."""
    NEGATIVE = {"sadness", "anger", "fear", "anxiety", "crisis", "stress"}
    PATHWAY = ["neutral", "anxiety", "sadness", "crisis"]

    # Check for pathway sub-sequence
    idx = 0
    for e in emotions:
        if e == PATHWAY[idx]:
            idx += 1
            if idx == len(PATHWAY):
                return True

    # Check 3+ consecutive negatives
    consec = 0
    for e in emotions:
        if e in NEGATIVE:
            consec += 1
            if consec >= 3:
                return True
        else:
            consec = 0

    return False


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return emotion analytics for the authenticated user."""

    stmt = (
        select(EmotionLog)
        .where(EmotionLog.user_id == user.id)
        .order_by(EmotionLog.created_at.desc())
        .limit(EMOTION_MEMORY_LIMIT)
    )
    result = await db.execute(stmt)
    logs: list[EmotionLog] = list(reversed(result.scalars().all()))

    emotion_trend = [
        EmotionPoint(
            timestamp=log.created_at.isoformat() if log.created_at else datetime.now(timezone.utc).isoformat(),
            emotion=log.primary_emotion,
            confidence=round(log.confidence, 4),
            is_high_risk=log.is_high_risk,
        )
        for log in logs
    ]

    emotion_list = [log.primary_emotion for log in logs]
    distribution_counter = Counter(emotion_list)
    emotion_distribution = [
        TriggerFrequency(emotion=e, count=c)
        for e, c in sorted(distribution_counter.items(), key=lambda x: x[1], reverse=True)
    ]

    risk_alerts = [
        RiskAlert(
            level="critical" if log.primary_emotion == "crisis" else "high",
            message=f"High-risk emotion '{log.primary_emotion}' detected.",
            timestamp=log.created_at.isoformat() if log.created_at else datetime.now(timezone.utc).isoformat(),
        )
        for log in logs
        if log.is_high_risk
    ]

    mood_trend = _detect_mood_trend(emotion_list)
    escalation = _detect_escalation(emotion_list)

    return DashboardResponse(
        emotion_trend=emotion_trend,
        emotion_distribution=emotion_distribution,
        risk_alerts=risk_alerts,
        mood_trend=mood_trend,
        escalation_detected=escalation,
        total_sessions=len(logs),
    )
