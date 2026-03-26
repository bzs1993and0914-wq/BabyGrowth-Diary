from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.daily_record import DailyRecord


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    account_tier: Mapped[str] = mapped_column(
        String(16), default="normal", nullable=False
    )  # normal | vip

    daily_records: Mapped[List["DailyRecord"]] = relationship(
        "DailyRecord", back_populates="user"
    )
