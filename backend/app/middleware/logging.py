"""Structured JSON request-logging middleware."""

from __future__ import annotations

import json
import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request as a structured JSON record.

    Accepts an incoming ``X-Request-ID`` header from the client (e.g. the
    frontend) and re-uses it as the request identifier so that a single
    logical operation can be traced end-to-end.  A fresh UUID is generated
    when the header is absent.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Prefer caller-supplied ID for end-to-end tracing; fall back to a fresh UUID.
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        t0 = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": latency_ms,
                }
            )
        )
        response.headers["X-Process-Time-Ms"] = str(latency_ms)
        response.headers["X-Request-ID"] = request_id
        return response
