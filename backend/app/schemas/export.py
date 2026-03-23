from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ExportRequest(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class ExportStatus(BaseModel):
    export_id: str
    status: str
    progress: float = 0.0
    file_path: Optional[str] = None
    error: Optional[str] = None


class StorageStats(BaseModel):
    total_records: int = 0
    total_media: int = 0
    total_images: int = 0
    total_videos: int = 0
    media_size_bytes: int = 0
    thumbnail_size_bytes: int = 0
    database_size_bytes: int = 0
    total_size_bytes: int = 0
