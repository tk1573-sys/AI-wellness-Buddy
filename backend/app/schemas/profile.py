"""UserProfile request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    age: int | None = Field(default=None, ge=10, le=120)
    gender: str | None = None
    occupation: str | None = None
    stress_level: int | None = Field(default=None, ge=1, le=10)
    sleep_pattern: str | None = None
    triggers: dict | None = None
    personality_type: str | None = None
    baseline_emotion: str | None = None
    exercise_frequency: str | None = None
    social_support: str | None = None
    coping_strategies: str | None = None
    # Extended personal history
    marital_status: str | None = None
    living_situation: str | None = None
    family_responsibilities: str | None = None
    family_background: str | None = None
    trauma_history: list[str] | None = None
    response_style: str | None = None
    safety_check: bool | None = None
    personal_triggers: list[str] | None = None
    language_preference: str | None = Field(default="english")
    # Guardian / emergency escalation settings
    enable_guardian_alerts: bool = False
    guardian_consent_given: bool = False
    guardian_name: str | None = None
    guardian_email: str | None = None
    guardian_whatsapp: str | None = None
    guardian_relationship: str | None = None


class ProfileUpdate(ProfileCreate):
    pass


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    age: int | None = None
    gender: str | None = None
    occupation: str | None = None
    stress_level: int | None = None
    sleep_pattern: str | None = None
    triggers: dict | None = None
    personality_type: str | None = None
    baseline_emotion: str | None = None
    exercise_frequency: str | None = None
    social_support: str | None = None
    coping_strategies: str | None = None
    # Extended personal history
    marital_status: str | None = None
    living_situation: str | None = None
    family_responsibilities: str | None = None
    family_background: str | None = None
    trauma_history: list[str] | None = None
    response_style: str | None = None
    safety_check: bool | None = None
    personal_triggers: list[str] | None = None
    language_preference: str | None = "english"
    # Guardian / emergency escalation settings
    enable_guardian_alerts: bool = False
    guardian_consent_given: bool = False
    guardian_name: str | None = None
    guardian_email: str | None = None
    guardian_whatsapp: str | None = None
    guardian_relationship: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
