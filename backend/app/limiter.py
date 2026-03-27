"""Shared SlowAPI rate-limiter instance.

Importing from a dedicated module avoids circular imports while still
allowing both the application factory (main.py) and individual routers
to reference the same Limiter object.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
    enabled=settings.RATELIMIT_ENABLED,
)
