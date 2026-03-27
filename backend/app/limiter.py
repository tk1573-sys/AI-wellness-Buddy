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
# Workaround: slowapi's get_app_config omits the cast argument when
# default_value is falsy, causing starlette.config.Config to return the raw
# environment-variable string (e.g. "false") instead of a proper bool.
# Re-applying the Pydantic-parsed value guarantees the correct type.
limiter.enabled = settings.RATELIMIT_ENABLED
