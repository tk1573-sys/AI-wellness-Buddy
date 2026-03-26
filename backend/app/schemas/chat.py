"""Chat request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None  # client may pass existing session id


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
    scores: list[dict] = []
