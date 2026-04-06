"""GuardianAlert ORM model — log of every alert dispatched to a guardian."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class GuardianAlert(Base):
    __tablename__ = "guardian_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Alert metadata
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)      # "email" | "whatsapp"
    delivery_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationship
    user: Mapped["User"] = relationship(back_populates="guardian_alerts")  # noqa: F821
