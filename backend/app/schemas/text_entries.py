from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class TextEntryCreate(BaseModel):
    daily_record_id: int
    content: str
    sort_order: int = 0


class TextEntryUpdate(BaseModel):
    content: Optional[str] = None
    sort_order: Optional[int] = None
