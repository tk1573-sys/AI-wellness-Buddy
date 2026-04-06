"""Analytics router — research-grade metrics for IEEE paper results.

Endpoint:
    GET /api/v1/analytics/research
        Returns emotion distribution, average confidence, average
        personalization score, risk trend, research summary, and
        export-ready plot data (base64 PNG).
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.limiter import limiter
from app.models.emotion import EmotionLog
from app.routers.auth import get_current_user
from app.services import analytics_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])
settings = get_settings()

# Maximum number of logs to analyse in a single request
_ANALYTICS_LOG_LIMIT = 500


# --------------------------------------------------------------------------- #
# Response schemas
# --------------------------------------------------------------------------- #

class EmotionDistributionItem(BaseModel):
    emotion: str
    count: int
    percentage: float


class RiskTrendPoint(BaseModel):
    date: str
    avg_risk_score: float


class ResearchSummary(BaseModel):
    total_sessions: int
    key_findings: list[str]
    improvement_percentage: float | None = None
    risk_detection_improvement: float | None = None
    confidence_improvement: float | None = None
    personalization_improvement: float | None = None
    insights: list[str]
    baseline_avg_risk: float | None = None
    current_avg_risk: float | None = None
    baseline_avg_confidence: float | None = None
    current_avg_confidence: float | None = None
    high_risk_session_rate_pct: float | None = None
    generated_at: str


class PlotData(BaseModel):
    emotion_distribution: str | None = None
    confidence_trend: str | None = None
    risk_progression: str | None = None


class ResearchAnalyticsResponse(BaseModel):
    emotion_distribution: list[EmotionDistributionItem]
    average_confidence: float
    average_personalization_score: float
    risk_trend: list[RiskTrendPoint]
    research_summary: ResearchSummary
    plot_data: PlotData
    total_sessions: int


# --------------------------------------------------------------------------- #
# Endpoint
# --------------------------------------------------------------------------- #

@router.get("/research", response_model=ResearchAnalyticsResponse)
@limiter.limit("10/minute")
async def get_research_analytics(
    request: Request,
    include_plots: bool = True,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
) -> Any:
    """Return research-grade analytics for the authenticated user's emotion logs.

    - **emotion_distribution**: Frequency and percentage per emotion label.
    - **average_confidence**: Mean prediction confidence across all sessions.
    - **average_personalization_score**: Mean personalization score (inverse
      uncertainty) across all sessions.
    - **risk_trend**: Daily average risk score, chronologically ordered.
    - **research_summary**: Auto-generated key findings, percentage improvements
      versus baseline, and plain-text insights suitable for an IEEE paper.
    - **plot_data**: Base64-encoded PNG images for emotion distribution bar
      chart, confidence trend line, and risk score progression (set
      ``include_plots=false`` to skip generation).
    - **total_sessions**: Number of emotion logs analysed.
    """
    stmt = (
        select(EmotionLog)
        .where(EmotionLog.user_id == user.id)
        .order_by(EmotionLog.created_at.asc())
        .limit(_ANALYTICS_LOG_LIMIT)
    )
    result = await db.execute(stmt)
    logs: list[EmotionLog] = list(result.scalars().all())

    emotion_distribution = [
        EmotionDistributionItem(**item)
        for item in analytics_service.compute_emotion_distribution(logs)
    ]
    avg_confidence = analytics_service.compute_average_confidence(logs)
    avg_personalization = analytics_service.compute_average_personalization_score(logs)
    risk_trend = [
        RiskTrendPoint(**point)
        for point in analytics_service.compute_risk_trend(logs)
    ]

    raw_summary = analytics_service.generate_research_summary(logs)
    research_summary = ResearchSummary(**raw_summary)

    # Persist summary to results/research_summary.json asynchronously-safe
    try:
        analytics_service.save_research_summary(raw_summary)
    except Exception:
        logger.warning("Could not persist research_summary.json", exc_info=True)

    plot_data_dict: dict[str, str | None] = {
        "emotion_distribution": None,
        "confidence_trend": None,
        "risk_progression": None,
    }
    if include_plots:
        try:
            plot_data_dict = analytics_service.generate_plots(logs)
        except Exception:
            logger.warning("Plot generation failed", exc_info=True)

    plot_data = PlotData(**plot_data_dict)

    return ResearchAnalyticsResponse(
        emotion_distribution=emotion_distribution,
        average_confidence=avg_confidence,
        average_personalization_score=avg_personalization,
        risk_trend=risk_trend,
        research_summary=research_summary,
        plot_data=plot_data,
        total_sessions=len(logs),
    )
