from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ParentWordCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    author_role: Optional[str] = None


class ParentWordUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    author_role: Optional[str] = None


class ParentWordListItem(BaseModel):
    id: int
    title: str
    content_preview: str
    author_role: Optional[str] = None
    media_count: int = 0
    first_thumbnail: Optional[str] = None
    created_at: str
    updated_at: str


class ParentWordResponse(BaseModel):
    id: int
    title: str
    content: str
    author_role: Optional[str] = None
    created_at: str
    updated_at: str
    media_entries: list = Field(default_factory=list)
    highlights: list = Field(default_factory=list)


class ParentWordListResponse(BaseModel):
    items: list[ParentWordListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class HighlightCreate(BaseModel):
    start_offset: int = Field(..., ge=0)
    end_offset: int = Field(..., ge=0)
    color: Optional[str] = "yellow"


class HighlightResponse(BaseModel):
    id: int
    start_offset: int
    end_offset: int
    color: Optional[str] = "yellow"
    created_at: str
