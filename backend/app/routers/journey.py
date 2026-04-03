"""Emotional Journey router.

Endpoint:
    GET /api/v1/journey  – emotion journey line, stress intensity gauge,
                           heatmap data, and stability metrics.
"""

from __future__ import annotations

import logging
import math
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.emotion import EmotionLog
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/journey", tags=["Journey"])

# Numeric severity map for stability calculations
_SEVERITY: dict[str, float] = {
    "joy": 0.1,
    "neutral": 0.2,
    "anxiety": 0.5,
    "fear": 0.55,
    "sadness": 0.6,
    "anger": 0.65,
    "stress": 0.7,
    "crisis": 1.0,
}

_JOURNEY_LOG_LIMIT = 50


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #

class JourneyPoint(BaseModel):
    timestamp: str
    emotion: str
    confidence: float
    risk_score: float
    is_high_risk: bool


class HeatmapCell(BaseModel):
    hour: int          # 0-23
    emotion: str
    intensity: float   # 0.0-1.0


class MovingAveragePoint(BaseModel):
    index: int
    avg_risk: float    # rolling 3-point average risk severity


class JourneyResponse(BaseModel):
    journey_points: list[JourneyPoint]
    heatmap: list[HeatmapCell]
    moving_average: list[MovingAveragePoint]
    latest_risk_score: float
    stability_index: float     # 1 = perfectly stable, 0 = highly volatile
    volatility_label: str      # "low" | "moderate" | "high"
    cdi_score: float           # Clinical Distress Index [0, 1]
    cdi_level: str             # "low" | "moderate" | "high" | "critical"
    total_points: int


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _to_risk(emotion: str, confidence: float) -> float:
    """Convert an emotion + confidence to a [0, 1] risk score."""
    severity = _SEVERITY.get(emotion.lower(), 0.3)
    return round(severity * confidence, 4)


def _stability_index(risk_scores: list[float]) -> float:
    """Compute a [0, 1] stability index (1 = perfectly stable)."""
    if len(risk_scores) < 2:
        return 1.0
    mean = sum(risk_scores) / len(risk_scores)
    variance = sum((x - mean) ** 2 for x in risk_scores) / len(risk_scores)
    std = math.sqrt(variance)
    # Normalize: std of 0.5 → stability 0; std of 0 → stability 1
    return round(max(0.0, 1.0 - std * 2), 4)


def _cdi(risk_scores: list[float], high_risk_count: int, total: int) -> float:
    """Compute a Clinical Distress Index as weighted risk mean + crisis proportion."""
    if not risk_scores:
        return 0.0
    avg_risk = sum(risk_scores) / len(risk_scores)
    crisis_rate = high_risk_count / max(total, 1)
    return round(min(1.0, avg_risk * 0.7 + crisis_rate * 0.3), 4)


def _moving_average(risk_scores: list[float], window: int = 3) -> list[MovingAveragePoint]:
    points: list[MovingAveragePoint] = []
    for i in range(len(risk_scores)):
        start = max(0, i - window + 1)
        chunk = risk_scores[start : i + 1]
        avg = round(sum(chunk) / len(chunk), 4)
        points.append(MovingAveragePoint(index=i + 1, avg_risk=avg))
    return points


def _build_heatmap(logs: list[EmotionLog]) -> list[HeatmapCell]:
    """Aggregate emotion intensity by hour of day."""
    buckets: dict[tuple[int, str], list[float]] = defaultdict(list)
    for log in logs:
        ts = log.created_at or datetime.now(timezone.utc)
        hour = ts.hour
        intensity = _to_risk(log.primary_emotion, log.confidence)
        buckets[(hour, log.primary_emotion)].append(intensity)

    cells: list[HeatmapCell] = []
    for (hour, emotion), intensities in sorted(buckets.items()):
        avg_intensity = round(sum(intensities) / len(intensities), 4)
        cells.append(HeatmapCell(hour=hour, emotion=emotion, intensity=avg_intensity))
    return cells


# --------------------------------------------------------------------------- #
# Endpoint
# --------------------------------------------------------------------------- #

@router.get("", response_model=JourneyResponse)
async def get_journey(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Return the emotional journey data for the authenticated user."""
    user = await get_current_user(token, db)

    stmt = (
        select(EmotionLog)
        .where(EmotionLog.user_id == user.id)
        .order_by(EmotionLog.created_at.desc())
        .limit(_JOURNEY_LOG_LIMIT)
    )
    result = await db.execute(stmt)
    logs: list[EmotionLog] = list(reversed(result.scalars().all()))

    journey_points: list[JourneyPoint] = []
    risk_scores: list[float] = []

    for log in logs:
        risk = _to_risk(log.primary_emotion, log.confidence)
        risk_scores.append(risk)
        journey_points.append(JourneyPoint(
            timestamp=(log.created_at or datetime.now(timezone.utc)).isoformat(),
            emotion=log.primary_emotion,
            confidence=round(log.confidence, 4),
            risk_score=risk,
            is_high_risk=log.is_high_risk,
        ))

    heatmap = _build_heatmap(logs)
    moving_avg = _moving_average(risk_scores)

    latest_risk = risk_scores[-1] if risk_scores else 0.0
    stability = _stability_index(risk_scores)
    high_risk_count = sum(1 for log in logs if log.is_high_risk)
    cdi_score = _cdi(risk_scores, high_risk_count, len(logs))

    volatility_label = (
        "low" if stability >= 0.7
        else "moderate" if stability >= 0.4
        else "high"
    )
    cdi_level = (
        "low" if cdi_score < 0.25
        else "moderate" if cdi_score < 0.5
        else "high" if cdi_score < 0.75
        else "critical"
    )

    logger.info(
        "journey user_id=%d points=%d stability=%.4f cdi=%.4f",
        user.id, len(logs), stability, cdi_score,
    )

    return JourneyResponse(
        journey_points=journey_points,
        heatmap=heatmap,
        moving_average=moving_avg,
        latest_risk_score=round(latest_risk, 4),
        stability_index=stability,
        volatility_label=volatility_label,
        cdi_score=cdi_score,
        cdi_level=cdi_level,
        total_points=len(logs),
    )
