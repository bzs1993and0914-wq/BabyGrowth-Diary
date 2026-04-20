from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.parent_word import ParentWord
    from app.models.user import User


class ParentWordHighlight(Base):
    __tablename__ = "parent_word_highlights"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_word_id: Mapped[int] = mapped_column(
        ForeignKey("parent_words.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_offset: Mapped[int] = mapped_column(nullable=False)
    end_offset: Mapped[int] = mapped_column(nullable=False)
    color: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="yellow")
    created_at: Mapped[str] = mapped_column(
        Text, default=lambda: datetime.now().isoformat()
    )

    parent_word: Mapped["ParentWord"] = relationship(
        "ParentWord", back_populates="highlights"
    )
    user: Mapped["User"] = relationship("User")
