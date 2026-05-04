"""Global request timeout middleware — returns HTTP 504 if a request exceeds the limit."""

from __future__ import annotations

import asyncio
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_SECONDS = 20


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Enforce a global per-request wall-clock timeout.

    If the downstream handler takes longer than REQUEST_TIMEOUT_SECONDS the
    middleware cancels it and returns HTTP 504 Gateway Timeout.
    Endpoint-level timeouts (e.g. asyncio.wait_for inside routers) remain
    intact and fire first; this middleware is the last-resort safety net.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(
                call_next(request), timeout=REQUEST_TIMEOUT_SECONDS
            )
        except asyncio.TimeoutError:
            logger.warning(
                "Request timeout: %s %s exceeded %ds",
                request.method,
                request.url.path,
                REQUEST_TIMEOUT_SECONDS,
            )
            return JSONResponse(
                status_code=504,
                content={"detail": "Request timeout"},
            )
