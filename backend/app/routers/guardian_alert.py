"""Guardian Alert router.

Endpoints:
  POST /api/v1/guardian-alert          — manually trigger a guardian alert
  GET  /api/v1/guardian-alert          — list alerts for the current user
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_user
from app.schemas.guardian_alert import (
    GuardianAlertListResponse,
    GuardianAlertResponse,
    GuardianAlertTriggerRequest,
)
from app.services import guardian_alert_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/guardian-alert", tags=["Guardian Alert"])


@router.post("", response_model=list[GuardianAlertResponse], status_code=status.HTTP_201_CREATED)
async def trigger_guardian_alert(
    req: GuardianAlertTriggerRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Trigger a guardian alert on the requested channel(s).

    The alert will only be dispatched if the authenticated user has:
    * ``enable_guardian_alerts = true`` in their profile
    * ``guardian_consent_given = true`` in their profile
    * A valid guardian email or WhatsApp number configured

    Returns the list of persisted alert log records.
    """
    logs = await guardian_alert_service.dispatch_guardian_alert(
        db,
        user_id=user.id,
        user_alias=user.username,
        risk_level=req.risk_level,
        risk_reason=req.risk_reason,
        channels=req.channels,
    )

    if not logs:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No alert was dispatched. Ensure guardian alerts are enabled, "
                "consent has been given, and guardian contact details are configured "
                "in your profile."
            ),
        )

    return [GuardianAlertResponse.model_validate(log) for log in logs]


@router.get("", response_model=GuardianAlertListResponse)
async def list_guardian_alerts(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return the authenticated user's guardian alert history (most recent first)."""
    alerts = await guardian_alert_service.get_alerts_for_user(db, user.id)
    return GuardianAlertListResponse(
        alerts=[GuardianAlertResponse.model_validate(a) for a in alerts],
        total=len(alerts),
    )
