from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SettingsResponse(BaseModel):
    theme: str = "default"
    dark_mode: bool = False
    thumbnail_max_size: int = 400
    thumbnail_quality: int = 85


class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    dark_mode: Optional[bool] = None
    thumbnail_max_size: Optional[int] = None
    thumbnail_quality: Optional[int] = None
