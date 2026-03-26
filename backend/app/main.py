"""
AI Wellness Buddy — FastAPI Application

Microservice architecture entry point.
Exposes:
  GET  /health
  POST /api/v1/auth/signup
  POST /api/v1/auth/login
  GET  /api/v1/auth/me
  POST /api/v1/predict
  POST /api/v1/chat
  GET  /api/v1/chat/history
"""

from __future__ import annotations

import json
import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import run_migrations
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import auth, chat, health, predict

settings = get_settings()

# --------------------------------------------------------------------------- #
# Logging configuration — JSON structured logs in production
# --------------------------------------------------------------------------- #


class _JsonFormatter(logging.Formatter):
    """Single-line JSON log records."""

    def format(self, record: logging.LogRecord) -> str:
        log: dict = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log["exc_info"] = traceback.format_exception(*record.exc_info)
        return json.dumps(log, ensure_ascii=False)
logger = logging.getLogger(__name__)

_handler = logging.StreamHandler()
_handler.setFormatter(_JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S"))
logging.root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logging.root.handlers = [_handler]


# --------------------------------------------------------------------------- #
# Application factory
# --------------------------------------------------------------------------- #

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        logger.info("Starting up %s v%s", settings.APP_NAME, settings.APP_VERSION)
        await run_migrations()
        logger.info("Database migrations applied.")
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
    # Rate limiting (100 req/min per IP)
    # ------------------------------------------------------------------ #
    app.add_middleware(RateLimitMiddleware)

    # ------------------------------------------------------------------ #
    # Request logging
    # ------------------------------------------------------------------ #
    app.add_middleware(RequestLoggingMiddleware)

    # ------------------------------------------------------------------ #
    # Routers
    # ------------------------------------------------------------------ #
    app.include_router(health.router)
    app.include_router(auth.router, prefix=settings.API_PREFIX)
    app.include_router(predict.router, prefix=settings.API_PREFIX)
    app.include_router(chat.router, prefix=settings.API_PREFIX)

    return app


app = create_app()
