"""Authentication router: signup, login, logout, current-user."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.limiter import limiter
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.services import auth_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()

# Cookie name used for the HttpOnly session token.
_AUTH_COOKIE = "wb_access_token"

# HTTP Bearer schemes — auto_error=True enforces auth; auto_error=False makes it optional.
_bearer = HTTPBearer(auto_error=False)
_bearer_optional = HTTPBearer(auto_error=False)


# --------------------------------------------------------------------------- #
# Cookie helpers
# --------------------------------------------------------------------------- #

def _set_auth_cookie(response: Response, token: str, max_age: int, *, request: Request) -> None:
    """Attach an HttpOnly, SameSite=Lax auth cookie to the response.

    The Secure flag is inferred from the request scheme: it is set only when
    the request arrived over HTTPS.  This makes the cookie work over plain HTTP
    in local development without any environment-variable configuration.
    """
    is_https = request.url.scheme == "https"
    response.set_cookie(
        key=_AUTH_COOKIE,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=is_https,  # True over HTTPS, False over HTTP (local dev)
        samesite="lax",   # lax allows cookie to be sent on same-site cross-port requests
        path="/",
    )


def _clear_auth_cookie(response: Response) -> None:
    """Remove the auth cookie by expiring it immediately."""
    response.delete_cookie(
        key=_AUTH_COOKIE,
        path="/",
        httponly=True,
        samesite="lax",
    )


# --------------------------------------------------------------------------- #
# Shared dependencies — resolve the current authenticated user.
# Accepts a JWT from either the HttpOnly cookie or the Authorization: Bearer
# header.  Cookie takes precedence; Bearer header serves as a fallback so
# existing API clients and tests continue to work.
# --------------------------------------------------------------------------- #

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    wb_access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Resolve an auth token (cookie or Bearer header) to a User row.
    Raises 401 on failure."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Log whether the auth cookie is present to aid debugging without
    # exposing sensitive session values in log output.
    logger.debug(
        "get_current_user: wb_access_token cookie present=%s",
        wb_access_token is not None,
    )

    # Prefer cookie; fall back to Authorization header.
    raw_token: str | None = wb_access_token or (
        credentials.credentials if credentials else None
    )
    if wb_access_token:
        logger.debug("get_current_user: token source=cookie")
    elif credentials and credentials.credentials:
        logger.debug("get_current_user: token source=bearer")
    if not raw_token:
        # Warn when the request arrived with no cookies at all — this is a
        # strong signal that the client isn't sending credentials (e.g.
        # withCredentials is missing from the axios/fetch call).
        if not request.cookies:
            logger.warning(
                "get_current_user: request has NO cookies at all — "
                "client may not be forwarding credentials. "
                "Ensure withCredentials=true (axios) or credentials='include' (fetch). "
                "Also verify ENV=development (HTTP) or HTTPS is in use."
            )
        logger.debug(
            "get_current_user: no auth cookie and no Bearer header — returning 401",
        )
        raise credentials_exception

    try:
        user_id = auth_service.decode_access_token(raw_token)
    except JWTError:
        logger.debug("get_current_user: JWT validation failed — invalid or expired token")
        raise credentials_exception

    logger.debug("get_current_user: JWT valid, user_id=%s", user_id)
    user = await auth_service.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        logger.debug("get_current_user: user_id=%s not found or inactive", user_id)
        raise credentials_exception
    logger.debug("get_current_user: authenticated user_id=%s email=%s", user.id, user.email)
    return user


async def get_optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_optional),
    wb_access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Like get_current_user but returns None for unauthenticated requests."""
    raw_token: str | None = wb_access_token or (
        credentials.credentials if credentials else None
    )
    if not raw_token:
        return None
    try:
        user_id = auth_service.decode_access_token(raw_token)
        user = await auth_service.get_user_by_id(db, user_id)
        return user if (user and user.is_active) else None
    except Exception:  # noqa: BLE001
        logger.debug("get_optional_user: token validation failed", exc_info=True)
        return None


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def signup(
    request: Request,
    req: SignupRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Register a new account, set an HttpOnly auth cookie, and return an access token."""
    existing = await auth_service.get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

    user = await auth_service.create_user(db, req)
    token, expire_seconds = auth_service.create_access_token(user.id)
    _set_auth_cookie(response, token, expire_seconds, request=request)
    logger.info("signup user_id=%d email=%s", user.id, user.email)
    return TokenResponse(access_token=token, expires_in=expire_seconds)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    req: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate, set an HttpOnly auth cookie, and return an access token."""
    user = await auth_service.get_user_by_email(db, req.email)
    if user is None or not auth_service.verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")

    token, expire_seconds = auth_service.create_access_token(user.id)
    _set_auth_cookie(response, token, expire_seconds, request=request)
    is_https = request.url.scheme == "https"
    logger.info("login user_id=%d", user.id)
    logger.debug(
        "login: cookie wb_access_token set (secure=%s samesite=lax path=/ max_age=%d)",
        is_https,
        expire_seconds,
    )
    return TokenResponse(access_token=token, expires_in=expire_seconds)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    """Invalidate the session by clearing the auth cookie."""
    _clear_auth_cookie(response)
    logger.info("logout — auth cookie cleared")


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return user


@router.get("/debug", include_in_schema=True, tags=["Auth"])
async def auth_debug(request: Request):
    """Return cookie presence flags for debugging the auth flow.

    This endpoint is intentionally unauthenticated so it can be called
    before a session is established.  It never exposes token *values* —
    only boolean presence flags.

    Use this to verify:
    - The browser is sending the wb_access_token cookie on requests.
    - The cookie was set correctly after login/signup.
    """
    return {
        "wb_access_token_present": _AUTH_COOKIE in request.cookies,
    }
