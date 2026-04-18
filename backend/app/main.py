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

# --- MUST BE FIRST ---
import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import logging
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("aiosqlite").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
# --- END ---

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
from app.utils import find_project_root

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
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
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

        # ── Pre-warm ML models ────────────────────────────────────────────
        # Load HuggingFace transformer models into the process-level pipeline
        # cache (models/emotion_transformer.py + emotion_analyzer.py) so that
        # the first real user request is served in <2 s instead of ~16 s.
        try:
            from app.services import emotion_service
            emotion_service._get_analyzer()
            logger.info("EmotionAnalyzer pre-warmed successfully.")
        except Exception:  # noqa: BLE001
            logger.warning(
                "EmotionAnalyzer pre-warm failed; first request may experience cold-start delay.",
                exc_info=True,
            )
        # Pre-warm the WellnessAgentPipeline.  The sentinel pipeline (user_id=0)
        # is discarded after construction, but the underlying HuggingFace models
        # now live in the module-level _PROCESS_PIPELINE_CACHE dicts so all
        # subsequent WellnessAgentPipeline() calls reuse them instantly.
        try:
            from app.services.chat_service import _get_pipeline, _pipelines
            _get_pipeline(0)
            _pipelines.pop(0, None)  # discard sentinel; models stay in cache
            logger.info("Model preloaded at startup — WellnessAgentPipeline pre-warmed.")
        except Exception:  # noqa: BLE001
            logger.warning(
                "WellnessAgentPipeline pre-warm failed; first request may experience cold-start delay.",
                exc_info=True,
            )

        # ── Voice pipeline readiness check ───────────────────────────────
        import shutil

        _ffmpeg_found = shutil.which("ffmpeg") is not None
        if _ffmpeg_found:
            logger.info("Voice pipeline ready — ffmpeg detected (%s).", shutil.which("ffmpeg"))
        else:
            logger.warning(
                "ffmpeg not found in PATH — WebM/MP3 audio from browsers cannot be "
                "converted for STT.  Install ffmpeg (apt-get install ffmpeg) for full "
                "voice support."
            )

        # Check gTTS / SpeechRecognition availability via VoiceHandler flags.
        # The voice router adds the project root to sys.path at module load, so
        # voice_handler is already importable here without extra path manipulation.
        try:
            from voice_handler import _GTTS_AVAILABLE, _SR_AVAILABLE  # noqa: PLC0415
            if _GTTS_AVAILABLE:
                logger.info("TTS ready — gTTS available.")
            else:
                logger.warning("TTS unavailable — gTTS not installed.")
            if _SR_AVAILABLE:
                logger.info("STT ready — SpeechRecognition available.")
            else:
                logger.warning("STT unavailable — SpeechRecognition not installed.")
        except Exception:  # noqa: BLE001
            logger.warning("Voice handler import check failed.", exc_info=True)

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

    # Warn when ALLOWED_ORIGINS mixes "localhost" and "127.0.0.1".
    # Mixing these causes the browser to treat the SameSite=Lax auth cookie
    # as cross-site (different host) and silently drop it on subsequent
    # requests, producing 401 errors after a successful login.
    _has_localhost = any("localhost" in o for o in allowed_origins)
    _has_127 = any("127.0.0.1" in o for o in allowed_origins)
    if _has_localhost and _has_127:
        logger.warning(
            "CORS: ALLOWED_ORIGINS contains both 'localhost' and '127.0.0.1'. "
            "Mixing these hostnames causes SameSite=Lax auth cookies to be "
            "treated as cross-site and silently dropped by the browser, "
            "breaking cookie-based auth after login. "
            "Use a single hostname consistently (recommend: 'localhost')."
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
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
