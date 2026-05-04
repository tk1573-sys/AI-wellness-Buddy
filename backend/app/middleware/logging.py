"""Structured JSON request-logging middleware."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request with method, path, status, latency, and request_id."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        t0 = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        logger.info(
            "%s %s -> %d  (%.1f ms) [req=%s]",
            request.method,
            request.url.path,
            response.status_code,
            latency_ms,
            request_id,
        )
        response.headers["X-Process-Time-Ms"] = str(latency_ms)
        response.headers["X-Request-ID"] = request_id
        return response
