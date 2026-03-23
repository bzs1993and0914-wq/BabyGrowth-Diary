from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class MilestoneCreate(BaseModel):
    daily_record_id: int
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None


class MilestoneResponse(BaseModel):
    id: int
    daily_record_id: int
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    icon: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    is_preset: bool = False

    model_config = {"from_attributes": True}
