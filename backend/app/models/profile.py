"""UserProfile ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )

    # Basic info
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(50), nullable=True)
    occupation: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Emotional profile
    stress_level: Mapped[int | None] = mapped_column(Integer, nullable=True)   # 1-10
    sleep_pattern: Mapped[str | None] = mapped_column(String(100), nullable=True)
    triggers: Mapped[dict | None] = mapped_column(JSON, nullable=True)          # e.g. {"work": true, "social": false}
    personality_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    baseline_emotion: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Lifestyle
    exercise_frequency: Mapped[str | None] = mapped_column(String(100), nullable=True)
    social_support: Mapped[str | None] = mapped_column(String(100), nullable=True)
    coping_strategies: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    user: Mapped["User"] = relationship(back_populates="profile")  # noqa: F821
