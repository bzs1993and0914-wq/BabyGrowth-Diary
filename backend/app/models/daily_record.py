from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.growth_metric import GrowthMetric
    from app.models.media_entry import MediaEntry
    from app.models.milestone import Milestone
    from app.models.text_entry import TextEntry
    from app.models.user import User


class DailyRecord(Base):
    __tablename__ = "daily_records"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_daily_record_user_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    use_default_media_placeholder: Mapped[bool] = mapped_column(default=False, nullable=False)
    allergy_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        Text, default=lambda: datetime.now().isoformat()
    )
    updated_at: Mapped[str] = mapped_column(
        Text,
        default=lambda: datetime.now().isoformat(),
        onupdate=lambda: datetime.now().isoformat(),
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="daily_records")

    media_entries: Mapped[List[MediaEntry]] = relationship(
        "MediaEntry",
        back_populates="daily_record",
        cascade="all, delete-orphan",
        order_by="MediaEntry.sort_order",
    )
    text_entries: Mapped[List[TextEntry]] = relationship(
        "TextEntry",
        back_populates="daily_record",
        cascade="all, delete-orphan",
        order_by="TextEntry.sort_order",
    )
    milestone: Mapped[Optional[Milestone]] = relationship(
        "Milestone",
        back_populates="daily_record",
        cascade="all, delete-orphan",
        uselist=False,
    )
    growth_metrics: Mapped[List[GrowthMetric]] = relationship(
        "GrowthMetric",
        back_populates="daily_record",
        cascade="all, delete-orphan",
    )
