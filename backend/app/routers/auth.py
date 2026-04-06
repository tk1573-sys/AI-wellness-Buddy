"""Authentication router: signup, login, current-user."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
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

# HTTP Bearer schemes — auto_error=True enforces auth; auto_error=False makes it optional.
_bearer = HTTPBearer(auto_error=True)
_bearer_optional = HTTPBearer(auto_error=False)


# --------------------------------------------------------------------------- #
# Shared dependencies — resolve the current authenticated user from the
# Authorization: Bearer <token> header.  Never read tokens from query strings.
# --------------------------------------------------------------------------- #

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
):
    """Resolve a Bearer token to a User row.  Raises 401 on failure."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = auth_service.decode_access_token(credentials.credentials)
    except JWTError:
        raise credentials_exception

    user = await auth_service.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_optional),
    db: AsyncSession = Depends(get_db),
):
    """Like get_current_user but returns None for unauthenticated requests."""
    if credentials is None:
        return None
    try:
        user_id = auth_service.decode_access_token(credentials.credentials)
        user = await auth_service.get_user_by_id(db, user_id)
        return user if (user and user.is_active) else None
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- #
# Endpoints
# --------------------------------------------------------------------------- #

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def signup(request: Request, req: SignupRequest, db: AsyncSession = Depends(get_db)):
    """Register a new account and return an access token."""
    existing = await auth_service.get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

    user = await auth_service.create_user(db, req)
    token, expire_seconds = auth_service.create_access_token(user.id)
    logger.info("signup user_id=%d email=%s", user.id, user.email)
    return TokenResponse(access_token=token, expires_in=expire_seconds)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(request: Request, req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and return an access token."""
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
    logger.info("login user_id=%d", user.id)
    return TokenResponse(access_token=token, expires_in=expire_seconds)


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return user
