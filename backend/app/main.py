"""
AI Wellness Buddy — FastAPI Application

Microservice architecture entry point.
Exposes:
  GET  /health
  GET  /metrics          (Prometheus)
  POST /api/v1/auth/signup
  POST /api/v1/auth/login
  POST /api/v1/auth/logout
  GET  /api/v1/auth/me
  POST /api/v1/predict
  POST /api/v1/chat
  GET  /api/v1/chat/history
  GET  /api/v1/analytics/research
  POST /api/v1/voice/transcribe
  POST /api/v1/voice/tts
  GET  /api/v1/weekly-report
  GET  /api/v1/journey
  GET  /api/v1/insights
  POST /api/v1/guardian-alert
  GET  /api/v1/guardian-alert
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import DisconnectionError, OperationalError, TimeoutError as SATimeoutError

from app.config import get_settings
from app.database import init_db
from app.limiter import limiter
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.routers import analytics, auth, chat, health, insights, predict, profile, dashboard, voice, weekly_report, journey, guardian_alert

try:
    settings = get_settings()
except Exception as _cfg_err:  # noqa: BLE001
    import sys
    # Print to stderr immediately so the error is visible in deployment logs
    # before the logging subsystem is configured.
    print(
        f"FATAL: Failed to load application settings — {_cfg_err}\n"
        "  Ensure all required environment variables are set "
        "(SECRET_KEY is mandatory).\n"
        "  Hint: copy backend/.env.example → backend/.env and fill in values.",
        file=sys.stderr,
        flush=True,
    )
    sys.exit(1)

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
        logger.info(
            "Config: env=%s debug=%s db=%s frontend_url=%r",
            settings.ENV,
            settings.DEBUG,
            settings.DATABASE_URL.split("://")[0] if "://" in settings.DATABASE_URL else "unknown",   # driver only — no creds
            settings.FRONTEND_URL or "(not set)",
        )
        await init_db()
        logger.info("Database tables created / verified.")
        # Pre-warm the ML model so the first real request is not delayed.
        try:
            from app.services import emotion_service
            emotion_service._get_analyzer()
            logger.info("EmotionAnalyzer pre-warmed successfully.")
        except Exception:  # noqa: BLE001
            logger.warning(
                "EmotionAnalyzer pre-warm failed; first request may experience cold-start delay.",
                exc_info=True,
            )
        # Pre-warm the WellnessAgentPipeline with a dummy user_id so the NLP
        # models and conversation templates are loaded before the first real
        # request.  A sentinel ID of 0 is used to avoid polluting real user
        # pipeline slots; the pipeline is discarded immediately after warming.
        try:
            from app.services.chat_service import _get_pipeline, _pipelines
            _get_pipeline(0)
            _pipelines.pop(0, None)  # discard the sentinel pipeline
            logger.info("WellnessAgentPipeline pre-warmed successfully.")
        except Exception:  # noqa: BLE001
            logger.warning(
                "WellnessAgentPipeline pre-warm failed; first request may experience cold-start delay.",
                exc_info=True,
            )
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
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ------------------------------------------------------------------ #
    # Rate limiter state + error handler
    # ------------------------------------------------------------------ #
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ------------------------------------------------------------------ #
    # DB outage handler — 503 for any SQLAlchemy connectivity failure.
    # Must be registered before the generic 500 handler so FastAPI's
    # most-specific-type matching picks it up first.
    # ------------------------------------------------------------------ #
    _DB_OUTAGE_RESPONSE = {
        "error": "database_unavailable",
        "message": "The service is temporarily unavailable. Please try again in a moment.",
        "status_code": 503,
    }

    @app.exception_handler(OperationalError)
    async def db_operational_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
        logger.error("DB operational error on %s %s: %s", request.method, request.url, exc)
        return JSONResponse(status_code=503, content=_DB_OUTAGE_RESPONSE)

    @app.exception_handler(DisconnectionError)
    async def db_disconnection_error_handler(request: Request, exc: DisconnectionError) -> JSONResponse:
        logger.error("DB disconnection on %s %s: %s", request.method, request.url, exc)
        return JSONResponse(status_code=503, content=_DB_OUTAGE_RESPONSE)

    @app.exception_handler(SATimeoutError)
    async def db_timeout_error_handler(request: Request, exc: SATimeoutError) -> JSONResponse:
        logger.error("DB timeout on %s %s: %s", request.method, request.url, exc)
        return JSONResponse(status_code=503, content=_DB_OUTAGE_RESPONSE)

    # ------------------------------------------------------------------ #
    # Global exception handler — returns a consistent JSON error shape
    # ------------------------------------------------------------------ #
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again later."},
        )

    # ------------------------------------------------------------------ #
    # Security headers
    # ------------------------------------------------------------------ #
    app.add_middleware(SecurityHeadersMiddleware, env=settings.ENV)

    # ------------------------------------------------------------------ #
    # CORS
    # ------------------------------------------------------------------ #
    allowed_origins = list(settings.ALLOWED_ORIGINS)
    if settings.FRONTEND_URL:
        allowed_origins.append(settings.FRONTEND_URL)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
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
    app.include_router(profile.router, prefix=settings.API_PREFIX)
    app.include_router(dashboard.router, prefix=settings.API_PREFIX)
    app.include_router(analytics.router, prefix=settings.API_PREFIX)
    app.include_router(voice.router, prefix=settings.API_PREFIX)
    app.include_router(weekly_report.router, prefix=settings.API_PREFIX)
    app.include_router(journey.router, prefix=settings.API_PREFIX)
    app.include_router(insights.router, prefix=settings.API_PREFIX)
    app.include_router(guardian_alert.router, prefix=settings.API_PREFIX)

    return app


app = create_app()
