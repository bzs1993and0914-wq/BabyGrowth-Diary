from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.daily_record import DailyRecord


class TextEntry(Base):
    __tablename__ = "text_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_record_id: Mapped[int] = mapped_column(
        ForeignKey("daily_records.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(
        Text, default=lambda: datetime.now().isoformat()
    )

    daily_record: Mapped[DailyRecord] = relationship(
        "DailyRecord", back_populates="text_entries"
    )
