from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class GrowthMetricCreate(BaseModel):
    daily_record_id: int
    metric_type: str = Field(..., pattern=r"^(height|weight|head_circumference)$")
    value: float
    unit: Optional[str] = None


class GrowthMetricResponse(BaseModel):
    id: int
    daily_record_id: int
    metric_type: str
    value: float
    unit: Optional[str] = None
    date: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


class GrowthCurveData(BaseModel):
    dates: List[str]
    values: List[float]
    metric_type: str
    unit: Optional[str] = None
