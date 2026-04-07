from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TextEntryInput(BaseModel):
    id: Optional[int] = None
    content: str
    sort_order: int = 0


class RecordCreate(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    texts: List[TextEntryInput] = []
    use_default_media_placeholder: bool = False
    allergy_notes: Optional[str] = None


class RecordUpdate(BaseModel):
    texts: List[TextEntryInput] = []
    use_default_media_placeholder: Optional[bool] = None
    allergy_notes: Optional[str] = None


class MediaEntryResponse(BaseModel):
    id: int
    media_type: str
    original_path: str
    thumbnail_path: Optional[str] = None
    description: Optional[str] = None
    file_size: Optional[int] = None
    original_filename: Optional[str] = None
    exif_date: Optional[str] = None
    sort_order: int = 0
    created_at: str

    model_config = {"from_attributes": True}


class TextEntryResponse(BaseModel):
    id: int
    content: str
    sort_order: int = 0
    created_at: str

    model_config = {"from_attributes": True}


class MilestoneInfo(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_icon: Optional[str] = None

    model_config = {"from_attributes": True}


class GrowthMetricResponse(BaseModel):
    id: int
    metric_type: str
    value: float
    unit: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}


class RecordResponse(BaseModel):
    id: int
    date: str
    created_at: str
    updated_at: str
    use_default_media_placeholder: bool = False
    allergy_notes: Optional[str] = None
    media_entries: List[MediaEntryResponse] = []
    text_entries: List[TextEntryResponse] = []
    milestone: Optional[MilestoneInfo] = None
    growth_metrics: List[GrowthMetricResponse] = []

    model_config = {"from_attributes": True}


class RecordListItem(BaseModel):
    date: str
    media_count: int = 0
    text_count: int = 0
    first_thumbnail: Optional[str] = None
    use_default_media_placeholder: bool = False
    allergy_notes: Optional[str] = None
    has_milestone: bool = False
    milestone_name: Optional[str] = None
    milestone_icon: Optional[str] = None
    preview_text: Optional[str] = None


class RecordListResponse(BaseModel):
    items: List[RecordListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
