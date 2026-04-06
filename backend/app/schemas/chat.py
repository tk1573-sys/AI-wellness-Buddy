"""Chat request/response schemas."""

from __future__ import annotations

from datetime import datetime

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.emotion import EmotionScore


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None  # client may pass existing session id
    language_preference: str | None = "english"  # english | tamil | bilingual


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    emotion: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    primary_emotion: str
    confidence: float = Field(ge=0.0, le=1.0)
    is_high_risk: bool
    escalation_message: str | None = None
    scores: list[EmotionScore] = []
    # Personalization fields
    personalization_score: float = Field(default=0.0, ge=0.0, le=1.0)
    used_triggers: list[str] = []
    response_type: Literal["generic", "personalized"] = "generic"
