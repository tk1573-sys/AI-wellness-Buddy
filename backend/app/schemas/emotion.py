"""Emotion prediction request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class EmotionScore(BaseModel):
    emotion: str
    score: float = Field(ge=0.0, le=1.0)


class PredictResponse(BaseModel):
    primary_emotion: str
    confidence: float = Field(ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0)
    is_uncertain: bool
    is_high_risk: bool
    escalation_message: str | None = None
    scores: list[EmotionScore]
    explanation: str | None = None
