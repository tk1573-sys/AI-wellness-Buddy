"""
AI Wellness Buddy — FastAPI Application

Microservice architecture entry point.
Exposes:
  GET  /health
  GET  /metrics          (Prometheus)
  POST /api/v1/auth/signup
  POST /api/v1/auth/login
  GET  /api/v1/auth/me
  POST /api/v1/predict
  POST /api/v1/chat
  GET  /api/v1/chat/history
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import get_settings
from app.database import init_db
from app.limiter import limiter
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.routers import auth, chat, health, predict

settings = get_settings()

# --------------------------------------------------------------------------- #
# Logging configuration
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Application factory
# --------------------------------------------------------------------------- #

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        logger.info("Starting up %s v%s", settings.APP_NAME, settings.APP_VERSION)
        await init_db()
        logger.info("Database tables created / verified.")
        yield
        logger.info("Shutting down.")

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Production-grade AI Wellness Buddy API — "
            "emotion detection, empathetic chat, and safety escalation."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ------------------------------------------------------------------ #
    # Rate limiter state + error handler
    # ------------------------------------------------------------------ #
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ------------------------------------------------------------------ #
    # Security headers
    # ------------------------------------------------------------------ #
    app.add_middleware(SecurityHeadersMiddleware)

    # ------------------------------------------------------------------ #
    # CORS
    # ------------------------------------------------------------------ #
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------ #
    # Request logging
    # ------------------------------------------------------------------ #
    app.add_middleware(RequestLoggingMiddleware)

    # ------------------------------------------------------------------ #
    # Prometheus metrics
    # ------------------------------------------------------------------ #
    Instrumentator(
        should_group_status_codes=True,
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    # ------------------------------------------------------------------ #
    # Routers
    # ------------------------------------------------------------------ #
    app.include_router(health.router)
    app.include_router(auth.router, prefix=settings.API_PREFIX)
    app.include_router(predict.router, prefix=settings.API_PREFIX)
    app.include_router(chat.router, prefix=settings.API_PREFIX)

    return app


app = create_app()

