"""Chat router — requires authentication."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.chat import ChatHistory
from app.routers.auth import get_current_user
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from app.services import chat_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message to the AI Wellness Buddy.

    Requires Bearer token authentication via the `token` query parameter.
    Returns the assistant's reply together with emotion analysis.
    """
    user = await get_current_user(token, db)
    return await chat_service.handle_chat(db, user.id, req)


@router.get("/history", response_model=list[ChatMessage])
async def history(
    token: str,
    session_id: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Return the authenticated user's chat history, optionally filtered by session."""
    user = await get_current_user(token, db)

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
