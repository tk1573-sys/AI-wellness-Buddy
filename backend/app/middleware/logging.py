"""Structured JSON request-logging middleware."""

from __future__ import annotations

import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request with method, path, status, and latency."""

    async def dispatch(self, request: Request, call_next) -> Response:
        t0 = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        logger.info(
            "%s %s -> %d  (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            latency_ms,
        )
        response.headers["X-Process-Time-Ms"] = str(latency_ms)
        return response
