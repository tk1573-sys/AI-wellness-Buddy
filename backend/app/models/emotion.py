"""EmotionLog ORM model."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    input_text: Mapped[str] = mapped_column(String(2000), nullable=False)
    primary_emotion: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    uncertainty: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_high_risk: Mapped[bool] = mapped_column(default=False, nullable=False)
    all_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Research analytics fields
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    personalization_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="emotion_logs")  # noqa: F821
