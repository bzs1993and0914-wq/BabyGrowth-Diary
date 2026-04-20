from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.daily_record import DailyRecord
    from app.models.parent_word import ParentWord


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    account_tier: Mapped[str] = mapped_column(
        String(16), default="normal", nullable=False
    )  # normal | vip
    parent_role: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    daily_records: Mapped[List["DailyRecord"]] = relationship(
        "DailyRecord", back_populates="user"
    )
    parent_words: Mapped[List["ParentWord"]] = relationship(
        "ParentWord", back_populates="user", cascade="all, delete-orphan"
    )
