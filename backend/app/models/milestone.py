from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.daily_record import DailyRecord
    from app.models.milestone_category import MilestoneCategory


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_record_id: Mapped[int] = mapped_column(
        ForeignKey("daily_records.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("milestone_categories.id"), nullable=True
    )
    name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        Text, default=lambda: datetime.now().isoformat()
    )

    daily_record: Mapped[DailyRecord] = relationship(
        "DailyRecord", back_populates="milestone"
    )
    category: Mapped[Optional[MilestoneCategory]] = relationship("MilestoneCategory")
