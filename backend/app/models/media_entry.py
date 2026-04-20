from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.daily_record import DailyRecord
    from app.models.parent_word import ParentWord


class MediaEntry(Base):
    __tablename__ = "media_entries"
    __table_args__ = (
        CheckConstraint("media_type IN ('image', 'video')", name="ck_media_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_record_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("daily_records.id", ondelete="CASCADE"), nullable=True
    )
    parent_word_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("parent_words.id", ondelete="CASCADE"), nullable=True
    )
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)
    original_path: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    original_filename: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exif_date: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(
        Text, default=lambda: datetime.now().isoformat()
    )

    daily_record: Mapped[Optional[DailyRecord]] = relationship(
        "DailyRecord", back_populates="media_entries"
    )
    parent_word: Mapped[Optional["ParentWord"]] = relationship(
        "ParentWord", back_populates="media_entries"
    )
