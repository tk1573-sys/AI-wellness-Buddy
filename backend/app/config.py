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
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    # Set this to your Vercel (or other) frontend URL so the browser
    # CORS preflight succeeds.  Example:
    #   FRONTEND_URL=https://ai-wellness-buddy.vercel.app
    FRONTEND_URL: str = ""

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

    # ------------------------------------------------------------------ #
    # Guardian Alert — email (SMTP / SendGrid-ready)
    # ------------------------------------------------------------------ #
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "no-reply@ai-wellness-buddy.app"

    # ------------------------------------------------------------------ #
    # Guardian Alert — WhatsApp (Twilio-ready)
    # ------------------------------------------------------------------ #
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = ""   # e.g. "+14155238886" (Twilio sandbox)

    # ------------------------------------------------------------------ #
    # Guardian Alert — escalation thresholds
    # ------------------------------------------------------------------ #
    # Minimum number of consecutive distress sessions before auto-alerting
    GUARDIAN_DISTRESS_SESSION_THRESHOLD: int = 3
    # Minimum risk-score spike (0-1 scale) that triggers an auto-alert
    GUARDIAN_RISK_SPIKE_THRESHOLD: float = 0.4
    # Minimum risk score required for a "high" risk_level to auto-trigger an alert.
    # Prevents marginal "high" emotion classifications from firing alerts.
    # "critical" always triggers regardless of score.
    GUARDIAN_HIGH_RISK_MIN_SCORE: float = 0.65
    # Minimum minutes that must pass between two successfully sent alerts for the
    # same user.  Prevents alert storms and duplicate notifications.
    GUARDIAN_ALERT_COOLDOWN_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
