from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.growth_metric import GrowthMetric
    from app.models.media_entry import MediaEntry
    from app.models.milestone import Milestone
    from app.models.text_entry import TextEntry


class DailyRecord(Base):
    __tablename__ = "daily_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    created_at: Mapped[str] = mapped_column(
        Text, default=lambda: datetime.now().isoformat()
    )
    updated_at: Mapped[str] = mapped_column(
        Text,
        default=lambda: datetime.now().isoformat(),
        onupdate=lambda: datetime.now().isoformat(),
    )

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
