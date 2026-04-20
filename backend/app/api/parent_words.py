from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.parent_word import ParentWord
from app.models.parent_word_highlight import ParentWordHighlight
from app.models.user import User
from app.schemas.parent_words import (
    HighlightCreate,
    HighlightResponse,
    ParentWordCreate,
    ParentWordListItem,
    ParentWordListResponse,
    ParentWordResponse,
    ParentWordUpdate,
)
from app.schemas.records import MediaEntryResponse
from app.services.storage_manager import cleanup_media_files

router = APIRouter(prefix="/parent-words", tags=["parent-words"])


def _parent_word_to_response(pw: ParentWord) -> ParentWordResponse:
    media_sorted = sorted(pw.media_entries, key=lambda m: m.sort_order)
    highlights_sorted = sorted(pw.highlights, key=lambda h: h.start_offset)
    return ParentWordResponse(
        id=pw.id,
        title=pw.title,
        content=pw.content,
        author_role=pw.author_role,
        created_at=pw.created_at,
        updated_at=pw.updated_at,
        media_entries=[MediaEntryResponse.model_validate(m) for m in media_sorted],
        highlights=[
            HighlightResponse(
                id=h.id,
                start_offset=h.start_offset,
                end_offset=h.end_offset,
                color=h.color,
                created_at=h.created_at,
            )
            for h in highlights_sorted
        ],
    )


@router.get("/", response_model=ParentWordListResponse)
async def list_parent_words(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    author_role: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    conditions = [ParentWord.user_id == current_user.id]
    if author_role is not None:
        conditions.append(ParentWord.author_role == author_role)

    count_result = await db.execute(
        select(func.count()).select_from(ParentWord).where(*conditions)
    )
    total = count_result.scalar() or 0

    total_pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size

    result = await db.execute(
        select(ParentWord)
        .where(*conditions)
        .options(selectinload(ParentWord.media_entries))
        .order_by(ParentWord.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    rows = result.scalars().all()

    items: list[ParentWordListItem] = []
    for pw in rows:
        first_thumb = None
        if pw.media_entries:
            for m in sorted(pw.media_entries, key=lambda x: x.sort_order):
                if m.thumbnail_path:
                    first_thumb = f"/api/media/{m.id}/thumbnail"
                    break
        items.append(
            ParentWordListItem(
                id=pw.id,
                title=pw.title,
                content_preview=pw.content[:80],
                author_role=pw.author_role,
                media_count=len(pw.media_entries),
                first_thumbnail=first_thumb,
                created_at=pw.created_at,
                updated_at=pw.updated_at,
            )
        )

    return ParentWordListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/", response_model=ParentWordResponse, status_code=201)
async def create_parent_word(
    data: ParentWordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pw = ParentWord(
        user_id=current_user.id,
        title=data.title,
        content=data.content,
        author_role=data.author_role
        if data.author_role is not None
        else current_user.parent_role,
    )
    db.add(pw)
    await db.commit()
    result = await db.execute(
        select(ParentWord)
        .options(selectinload(ParentWord.media_entries), selectinload(ParentWord.highlights))
        .where(ParentWord.id == pw.id)
    )
    created = result.scalars().first()
    return _parent_word_to_response(created)


@router.get("/{word_id}", response_model=ParentWordResponse)
async def get_parent_word(
    word_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ParentWord)
        .options(selectinload(ParentWord.media_entries), selectinload(ParentWord.highlights))
        .where(
            ParentWord.id == word_id,
            ParentWord.user_id == current_user.id,
        )
    )
    pw = result.scalars().first()
    if not pw:
        raise HTTPException(status_code=404, detail="Parent word not found")
    return _parent_word_to_response(pw)


@router.put("/{word_id}", response_model=ParentWordResponse)
async def update_parent_word(
    word_id: int,
    data: ParentWordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ParentWord).where(
            ParentWord.id == word_id,
            ParentWord.user_id == current_user.id,
        )
    )
    pw = result.scalars().first()
    if not pw:
        raise HTTPException(status_code=404, detail="Parent word not found")

    update_payload = data.model_dump(exclude_unset=True)
    for key, value in update_payload.items():
        if value is not None:
            setattr(pw, key, value)
    pw.updated_at = datetime.now().isoformat()

    await db.commit()

    result = await db.execute(
        select(ParentWord)
        .options(selectinload(ParentWord.media_entries), selectinload(ParentWord.highlights))
        .where(ParentWord.id == word_id)
    )
    updated = result.scalars().first()
    return _parent_word_to_response(updated)


@router.delete("/{word_id}", status_code=204)
async def delete_parent_word(
    word_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ParentWord)
        .options(selectinload(ParentWord.media_entries))
        .where(
            ParentWord.id == word_id,
            ParentWord.user_id == current_user.id,
        )
    )
    pw = result.scalars().first()
    if not pw:
        raise HTTPException(status_code=404, detail="Parent word not found")

    for entry in pw.media_entries:
        cleanup_media_files(entry.original_path, entry.thumbnail_path)

    await db.delete(pw)
    await db.commit()


@router.post("/{word_id}/highlights", response_model=HighlightResponse, status_code=201)
async def add_highlight(
    word_id: int,
    data: HighlightCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ParentWord).where(
            ParentWord.id == word_id,
            ParentWord.user_id == current_user.id,
        )
    )
    pw = result.scalars().first()
    if not pw:
        raise HTTPException(status_code=404, detail="Parent word not found")

    if data.start_offset >= data.end_offset:
        raise HTTPException(status_code=400, detail="start_offset must be less than end_offset")
    if data.end_offset > len(pw.content):
        raise HTTPException(status_code=400, detail="end_offset exceeds content length")

    highlight = ParentWordHighlight(
        parent_word_id=word_id,
        user_id=current_user.id,
        start_offset=data.start_offset,
        end_offset=data.end_offset,
        color=data.color or "yellow",
    )
    db.add(highlight)
    await db.commit()
    await db.refresh(highlight)
    return HighlightResponse(
        id=highlight.id,
        start_offset=highlight.start_offset,
        end_offset=highlight.end_offset,
        color=highlight.color,
        created_at=highlight.created_at,
    )


@router.delete("/{word_id}/highlights/{highlight_id}", status_code=204)
async def remove_highlight(
    word_id: int,
    highlight_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ParentWordHighlight).where(
            ParentWordHighlight.id == highlight_id,
            ParentWordHighlight.parent_word_id == word_id,
            ParentWordHighlight.user_id == current_user.id,
        )
    )
    highlight = result.scalars().first()
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")

    await db.delete(highlight)
    await db.commit()
