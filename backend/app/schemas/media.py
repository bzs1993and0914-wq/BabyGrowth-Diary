from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class MediaUploadResponse(BaseModel):
    id: int
    daily_record_id: Optional[int] = None
    parent_word_id: Optional[int] = None
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


class MediaUpdate(BaseModel):
    description: Optional[str] = None
    sort_order: Optional[int] = None
