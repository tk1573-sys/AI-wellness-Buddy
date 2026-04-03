"""
Application configuration loaded from environment variables.

All settings have sensible defaults for local development.  In production
supply the values via a .env file or real environment variables so that
secrets never appear in source code.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_NAME: str = "AI Wellness Buddy"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # ------------------------------------------------------------------ #
    # API
    # ------------------------------------------------------------------ #
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    # ------------------------------------------------------------------ #
    # Security / JWT
    # ------------------------------------------------------------------ #
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = "sqlite+aiosqlite:///./wellness.db"
    # For PostgreSQL use: postgresql+asyncpg://user:pass@host:5432/dbname

    # ------------------------------------------------------------------ #
    # Safety layer
    # ------------------------------------------------------------------ #
    CRISIS_CONFIDENCE_THRESHOLD: float = 0.6
    HIGH_RISK_ESCALATION_MESSAGE: str = (
        "I'm concerned about your wellbeing. "
        "Please reach out to a professional: "
        "988 Suicide & Crisis Lifeline (call or text 988) or "
        "Crisis Text Line (text HOME to 741741)."
    )

    # ------------------------------------------------------------------ #
    # Rate limiting (slowapi / limits syntax)
    # ------------------------------------------------------------------ #
    RATELIMIT_ENABLED: bool = True
    RATE_LIMIT_AUTH: str = "5/minute"      # signup + login
    RATE_LIMIT_PREDICT: str = "30/minute"  # emotion prediction
    RATE_LIMIT_CHAT: str = "20/minute"     # chat messages

    # ------------------------------------------------------------------ #
    # Environment
    # ------------------------------------------------------------------ #
    ENV: str = "development"

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
