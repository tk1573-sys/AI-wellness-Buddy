"""Health check router."""

from fastapi import APIRouter
from app.config import get_settings

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
