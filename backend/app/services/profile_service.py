"""Profile service — CRUD for UserProfile."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate


async def get_profile(db: AsyncSession, user_id: int) -> UserProfile | None:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_profile(
    db: AsyncSession,
    user_id: int,
    data: ProfileCreate,
) -> UserProfile:
    profile = UserProfile(user_id=user_id, **data.model_dump(exclude_unset=False))
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def upsert_profile(
    db: AsyncSession,
    user_id: int,
    data: ProfileCreate | ProfileUpdate,
) -> UserProfile:
    existing = await get_profile(db, user_id)
    if existing is None:
        return await create_profile(db, user_id, data)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    await db.commit()
    await db.refresh(existing)
    return existing
