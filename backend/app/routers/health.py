"""Health check router."""

import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.services import emotion_service

router = APIRouter(tags=["Health"])
settings = get_settings()
_logger = logging.getLogger(__name__)


@router.get("/health")
async def health():
    """Liveness probe used by load balancers and deployment platforms."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/health/full")
async def health_full():
    """Readiness probe — checks DB connectivity and ML model state.

    Always returns HTTP 200 so that monitoring tools can always read the
    JSON body.  Individual component failures are reflected in the body
    rather than the status code, keeping this endpoint non-disruptive.
    """
    db_ok = False
    db_error: str | None = None
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:  # noqa: BLE001
        # Log the real error internally; expose only a safe generic message.
        _logger.warning("Health check DB probe failed: %s", exc)
        db_error = "Database connection failed"

    model_loaded = emotion_service.is_model_loaded()

    return {
        "status": "ok",
        "db": {"ok": db_ok, "error": db_error},
        "model_loaded": model_loaded,
    }
