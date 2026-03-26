"""Authentication service: JWT creation/verification and password management."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.schemas.auth import SignupRequest

settings = get_settings()


# --------------------------------------------------------------------------- #
# Password helpers
# --------------------------------------------------------------------------- #

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False


# --------------------------------------------------------------------------- #
# JWT helpers
# --------------------------------------------------------------------------- #

def create_access_token(subject: int | str) -> tuple[str, int]:
    """Return (encoded_jwt, expire_seconds)."""
    expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expire = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)
    payload = {"sub": str(subject), "exp": expire, "iat": datetime.now(timezone.utc)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire_seconds


def decode_access_token(token: str) -> int:
    """Decode a JWT and return the user id.  Raises ``JWTError`` on failure."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    sub = payload.get("sub")
    if sub is None:
        raise JWTError("Missing subject claim")
    return int(sub)


# --------------------------------------------------------------------------- #
# Database helpers
# --------------------------------------------------------------------------- #

async def create_user(db: AsyncSession, req: SignupRequest) -> User:
    user = User(
        email=req.email,
        username=req.username,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()
