from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.media_entry import MediaEntry
    from app.models.parent_word_highlight import ParentWordHighlight
    from app.models.user import User


class ParentWord(Base):
    __tablename__ = "parent_words"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_role: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        Text, default=lambda: datetime.now().isoformat()
    )
    updated_at: Mapped[str] = mapped_column(
        Text,
        default=lambda: datetime.now().isoformat(),
        onupdate=lambda: datetime.now().isoformat(),
    )

    user: Mapped["User"] = relationship("User", back_populates="parent_words")
    media_entries: Mapped[List["MediaEntry"]] = relationship(
        "MediaEntry",
        back_populates="parent_word",
        cascade="all, delete-orphan",
        order_by="MediaEntry.sort_order",
    )
    highlights: Mapped[List["ParentWordHighlight"]] = relationship(
        "ParentWordHighlight",
        back_populates="parent_word",
        cascade="all, delete-orphan",
        order_by="ParentWordHighlight.start_offset",
    )
