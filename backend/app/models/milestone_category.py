from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class MilestoneCategory(Base):
    __tablename__ = "milestone_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False)
