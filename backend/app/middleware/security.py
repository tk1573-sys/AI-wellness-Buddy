"""Security headers middleware.

Adds standard HTTP security headers to every response to protect against
common web vulnerabilities (XSS, clickjacking, MIME sniffing, etc.).

In production (ENV=production) a strict Content-Security-Policy is applied.
In all other environments (development, staging, …) a relaxed policy is used
so that the Swagger UI served at /docs can load its assets.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

# Strict CSP for production — no inline scripts, no external sources.
_CSP_PRODUCTION = "default-src 'none'; frame-ancestors 'none'"

# Targeted relaxed CSP for non-production environments.
# Swagger UI requires 'unsafe-inline' for its scripts and styles, and
# 'unsafe-eval' for its dynamic code evaluation.  Data URIs are needed
# for its embedded favicon/images.  All other sources default to 'self'.
_CSP_DEVELOPMENT = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)

# Paths whose responses must never have a restrictive CSP that would break the
# browser-rendered docs UI.
_DOCS_PATHS = frozenset({"/docs", "/redoc", "/openapi.json"})


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject security headers into every HTTP response.

    Parameters
    ----------
    app:
        The ASGI application to wrap.
    env:
        The deployment environment.  Pass ``"production"`` to enable the
        strict Content-Security-Policy.  Any other value (the default,
        ``"development"``) uses the relaxed policy required by Swagger UI.
    """

    def __init__(self, app: ASGIApp, env: str = "development") -> None:
        super().__init__(app)
        self._is_production = env.lower() == "production"

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Deny framing entirely (clickjacking protection)
        response.headers["X-Frame-Options"] = "DENY"

        # Enable browser XSS filter (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Enforce HTTPS for 1 year (HSTS) — only meaningful behind TLS
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Restrict referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content-Security-Policy:
        #   • production  → strict (blocks everything not explicitly allowed)
        #   • development → relaxed (Swagger UI needs inline scripts/styles)
        #   Docs paths always use the relaxed policy regardless of environment
        #   so the browser-rendered UI functions correctly.
        if self._is_production and request.url.path not in _DOCS_PATHS:
            csp = _CSP_PRODUCTION
        else:
            csp = _CSP_DEVELOPMENT
        response.headers["Content-Security-Policy"] = csp

        # Disable browser features not needed by a REST API
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response
