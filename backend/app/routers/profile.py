"""Profile router — requires authentication."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_user
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services import profile_service

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.post("", response_model=ProfileResponse, status_code=201)
async def create_profile(
    data: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create or overwrite the authenticated user's profile."""
    profile = await profile_service.upsert_profile(db, user.id, data)
    return ProfileResponse.model_validate(profile)


@router.get("", response_model=ProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return the authenticated user's profile."""
    profile = await profile_service.get_profile(db, user.id)
    if profile is None:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    return ProfileResponse.model_validate(profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Update the authenticated user's profile (partial update supported)."""
    profile = await profile_service.upsert_profile(db, user.id, data)
    return ProfileResponse.model_validate(profile)
