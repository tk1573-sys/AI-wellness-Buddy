"""Health check router."""

from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.services import emotion_service

router = APIRouter(tags=["Health"])
settings = get_settings()


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
        db_error = str(exc)

    model_loaded = emotion_service._analyzer is not None

    return {
        "status": "ok",
        "db": {"ok": db_ok, "error": db_error},
        "model_loaded": model_loaded,
    }
