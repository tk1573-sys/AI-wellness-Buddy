"""Simple in-process sliding-window rate limiter.

Limits each client IP to ``RATE_LIMIT_REQUESTS`` requests per
``RATE_LIMIT_WINDOW_SECONDS`` seconds.  When the limit is exceeded the
middleware responds immediately with HTTP 429 without forwarding the
request to the application.

This implementation is suitable for a single-process deployment.  For
multi-worker or distributed setups replace the in-memory store with a
shared Redis back-end.
"""

from __future__ import annotations

import collections
import logging
import time

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.rate_limit")

# Default limits — override via subclass or monkey-patch for tests.
RATE_LIMIT_REQUESTS: int = 100
RATE_LIMIT_WINDOW_SECONDS: int = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter keyed by client IP address."""

    def __init__(self, app, requests: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW_SECONDS):
        super().__init__(app)
        self._requests = requests
        self._window = window
        # Maps IP → deque of request timestamps
        self._hits: dict[str, collections.deque[float]] = collections.defaultdict(
            lambda: collections.deque()
        )

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next) -> Response:
        # Health check endpoint is exempt from rate limiting.
        if request.url.path == "/health":
            return await call_next(request)

        ip = self._get_client_ip(request)
        now = time.monotonic()
        window_start = now - self._window
        dq = self._hits[ip]

        # Evict timestamps outside the window.
        while dq and dq[0] < window_start:
            dq.popleft()

        if len(dq) >= self._requests:
            retry_after = int(self._window - (now - dq[0])) + 1
            logger.warning("rate_limit_exceeded ip=%s count=%d", ip, len(dq))
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": str(retry_after)},
            )

        dq.append(now)
        return await call_next(request)
