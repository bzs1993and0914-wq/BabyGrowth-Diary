from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base

if TYPE_CHECKING:
    from app.models.daily_record import DailyRecord


class GrowthMetric(Base):
    __tablename__ = "growth_metrics"
    __table_args__ = (
        CheckConstraint(
            "metric_type IN ('height', 'weight', 'head_circumference')",
            name="ck_metric_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    daily_record_id: Mapped[int] = mapped_column(
        ForeignKey("daily_records.id", ondelete="CASCADE"), nullable=False
    )
    metric_type: Mapped[str] = mapped_column(String(20), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[str] = mapped_column(
        Text, default=lambda: datetime.now().isoformat()
    )

    daily_record: Mapped[DailyRecord] = relationship(
        "DailyRecord", back_populates="growth_metrics"
    )
