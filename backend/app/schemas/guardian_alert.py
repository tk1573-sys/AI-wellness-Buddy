"""Schemas for guardian alert endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GuardianAlertTriggerRequest(BaseModel):
    """Manually trigger a guardian alert (e.g. from the API)."""

    risk_level: Literal["high", "critical"] = "high"
    risk_reason: str | None = Field(default=None, max_length=500)
    channels: list[Literal["email", "whatsapp"]] = Field(default=["email"])


class GuardianAlertResponse(BaseModel):
    id: int
    user_id: int
    risk_level: str
    risk_reason: str | None = None
    channel: str
    delivery_status: str
    timestamp: datetime

    model_config = {"from_attributes": True}


class GuardianAlertListResponse(BaseModel):
    alerts: list[GuardianAlertResponse]
    total: int
