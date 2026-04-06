"""Chat router — requires authentication."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.limiter import limiter
from app.models.chat import ChatHistory
from app.routers.auth import get_current_user
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from app.services import chat_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])
settings = get_settings()


@router.post("", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT_CHAT)
async def chat(
    request: Request,
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Send a message to the AI Wellness Buddy.

    Requires Bearer token authentication via the Authorization header.
    Returns the assistant's reply together with emotion analysis.
    """
    return await chat_service.handle_chat(db, user.id, req)


@router.get("/history", response_model=list[ChatMessage])
async def history(
    session_id: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return the authenticated user's chat history, optionally filtered by session."""
    stmt = (
        select(ChatHistory)
        .where(ChatHistory.user_id == user.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(max(1, min(limit, 200)))
    )
    if session_id:
        stmt = stmt.where(ChatHistory.session_id == session_id)

    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [ChatMessage.model_validate(row) for row in reversed(rows)]
