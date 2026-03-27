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
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
