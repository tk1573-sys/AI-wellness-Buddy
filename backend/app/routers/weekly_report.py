"""Weekly Report router.

Endpoint:
    GET /api/v1/weekly-report  – summary of the past 7 days of emotion logs

Returns a narrative summary, daily emotion counts, dominant emotions,
and session list for the authenticated user.
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.emotion import EmotionLog
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weekly-report", tags=["Weekly Report"])

_NEGATIVE = {"sadness", "anger", "fear", "anxiety", "crisis", "stress"}
_POSITIVE = {"joy", "neutral"}


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #

class DailyCount(BaseModel):
    date: str          # ISO date string "YYYY-MM-DD"
    count: int
    dominant_emotion: str
    avg_confidence: float


class SessionSummary(BaseModel):
    timestamp: str
    dominant_emotion: str
    confidence: float
    is_high_risk: bool


class EmotionCount(BaseModel):
    emotion: str
    count: int


class WeeklyReportResponse(BaseModel):
    summary_text: str
    daily_breakdown: list[DailyCount]
    session_summaries: list[SessionSummary]
    emotion_distribution: list[EmotionCount]
    total_sessions: int
    high_risk_count: int
    dominant_emotion_week: str
    mood_direction: str  # "improving" | "stable" | "declining"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _mood_direction(emotions: list[str]) -> str:
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


def _generate_summary(
    total: int,
    high_risk: int,
    dominant: str,
    direction: str,
    distribution: list[EmotionCount],
) -> str:
    if total == 0:
        return (
            "No data was recorded in the past 7 days. "
            "Start chatting to build your weekly report."
        )

    parts: list[str] = []
    parts.append(
        f"This week you had **{total}** recorded emotion{'s' if total != 1 else ''}. "
    )

    if dominant in _POSITIVE:
        parts.append(
            f"Your most frequent emotional state was **{dominant}** — a positive sign. "
        )
    else:
        parts.append(
            f"Your most frequent emotional state was **{dominant}**. "
            "It's important to acknowledge these feelings and reach out if needed. "
        )

    if direction == "improving":
        parts.append("Your mood trend shows **improvement** over the week. 📈 ")
    elif direction == "declining":
        parts.append(
            "Your mood shows a **declining trend** this week. "
            "Consider speaking to a professional or a trusted person. 📉 "
        )
    else:
        parts.append("Your mood has been **relatively stable** this week. ➡️ ")

    if high_risk > 0:
        parts.append(
            f"⚠️ There {'was' if high_risk == 1 else 'were'} **{high_risk}** "
            f"high-risk moment{'s' if high_risk != 1 else ''} detected. "
            "Please do not hesitate to contact the 988 Suicide & Crisis Lifeline. "
        )

    top_emotions = [ec.emotion for ec in distribution[:3]]
    if top_emotions:
        parts.append(
            f"The top emotions detected were: {', '.join(top_emotions)}."
        )

    return "".join(parts)


# --------------------------------------------------------------------------- #
# Endpoint
# --------------------------------------------------------------------------- #

@router.get("", response_model=WeeklyReportResponse)
async def get_weekly_report(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return a 7-day emotional wellness report for the authenticated user."""

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    stmt = (
        select(EmotionLog)
        .where(EmotionLog.user_id == user.id)
        .where(EmotionLog.created_at >= cutoff)
        .order_by(EmotionLog.created_at.asc())
    )
    result = await db.execute(stmt)
    logs: list[EmotionLog] = list(result.scalars().all())

    # ── Aggregate by day ────────────────────────────────────────────────────
    daily_buckets: dict[str, list[EmotionLog]] = defaultdict(list)
    for log in logs:
        day = (log.created_at or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
        daily_buckets[day].append(log)

    daily_breakdown: list[DailyCount] = []
    for day in sorted(daily_buckets.keys()):
        day_logs = daily_buckets[day]
        counter = Counter(l.primary_emotion for l in day_logs)
        dominant = counter.most_common(1)[0][0] if counter else "neutral"
        avg_conf = round(sum(l.confidence for l in day_logs) / len(day_logs), 4)
        daily_breakdown.append(DailyCount(
            date=day,
            count=len(day_logs),
            dominant_emotion=dominant,
            avg_confidence=avg_conf,
        ))

    # ── Session summaries (individual log entries) ─────────────────────────
    session_summaries = [
        SessionSummary(
            timestamp=(log.created_at or datetime.now(timezone.utc)).isoformat(),
            dominant_emotion=log.primary_emotion,
            confidence=round(log.confidence, 4),
            is_high_risk=log.is_high_risk,
        )
        for log in logs
    ]

    # ── Overall distribution ────────────────────────────────────────────────
    emotion_counter = Counter(log.primary_emotion for log in logs)
    distribution = [
        EmotionCount(emotion=e, count=c)
        for e, c in sorted(emotion_counter.items(), key=lambda x: x[1], reverse=True)
    ]

    emotion_list = [log.primary_emotion for log in logs]
    dominant_week = distribution[0].emotion if distribution else "neutral"
    high_risk_count = sum(1 for log in logs if log.is_high_risk)
    direction = _mood_direction(emotion_list)
    summary_text = _generate_summary(
        len(logs), high_risk_count, dominant_week, direction, distribution
    )

    logger.info(
        "weekly-report user_id=%d logs=%d high_risk=%d direction=%s",
        user.id, len(logs), high_risk_count, direction,
    )

    return WeeklyReportResponse(
        summary_text=summary_text,
        daily_breakdown=daily_breakdown,
        session_summaries=session_summaries,
        emotion_distribution=distribution,
        total_sessions=len(logs),
        high_risk_count=high_risk_count,
        dominant_emotion_week=dominant_week,
        mood_direction=direction,
    )
