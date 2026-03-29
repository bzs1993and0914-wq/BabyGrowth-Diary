from __future__ import annotations

import math
from datetime import date as date_type, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.daily_record import DailyRecord
from app.models.media_entry import MediaEntry
from app.models.milestone import Milestone
from app.models.text_entry import TextEntry
from app.models.user import User
from app.schemas.records import (
    GrowthMetricResponse,
    MediaEntryResponse,
    MilestoneInfo,
    RecordCreate,
    RecordListItem,
    RecordListResponse,
    RecordResponse,
    RecordUpdate,
    TextEntryResponse,
)
from app.services.storage_manager import cleanup_media_files

router = APIRouter(prefix="/records", tags=["records"])


@router.get("/", response_model=RecordListResponse)
async def list_records(
    current_user: User = Depends(get_current_user),
    view: str = Query("day", pattern="^(day|week|month|year)$"),
    date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    milestone_only: bool = Query(False),
    q: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """分页查询当前用户的每日记录列表，支持按时间粒度、关键词、日期范围、里程碑过滤。

    - view=week/month/year 时根据 date 参数计算对应时间区间
    - q 在文字记录内容和里程碑名称中进行模糊匹配
    - 返回每条记录的缩略图、文字预览、里程碑概要（不含完整媒体列表）
    """
    query = (
        select(DailyRecord)
        .where(DailyRecord.user_id == current_user.id)
        .options(
            selectinload(DailyRecord.media_entries),
            selectinload(DailyRecord.text_entries),
            selectinload(DailyRecord.milestone).selectinload(Milestone.category),
        )
        .order_by(DailyRecord.date.desc())
    )

    if date and view != "day":
        d = date_type.fromisoformat(date)
        if view == "week":
            start = d - timedelta(days=d.weekday())
            end = start + timedelta(days=6)
        elif view == "month":
            start = d.replace(day=1)
            next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
            end = next_month - timedelta(days=1)
        else:
            start = d.replace(month=1, day=1)
            end = d.replace(month=12, day=31)
        query = query.where(
            DailyRecord.date >= start.isoformat(),
            DailyRecord.date <= end.isoformat(),
        )
    elif date and view == "day":
        query = query.where(DailyRecord.date == date)

    if date_from:
        query = query.where(DailyRecord.date >= date_from)
    if date_to:
        query = query.where(DailyRecord.date <= date_to)

    if milestone_only:
        query = query.where(DailyRecord.milestone.has())

    if q:
        keyword = f"%{q}%"
        query = query.where(
            DailyRecord.id.in_(
                select(TextEntry.daily_record_id).where(TextEntry.content.like(keyword))
            )
            | DailyRecord.id.in_(
                select(Milestone.daily_record_id).where(Milestone.name.like(keyword))
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    total_pages = max(1, math.ceil(total / page_size))
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    records = result.scalars().all()
    
    items: List[RecordListItem] = []
    for rec in records:
        first_thumb = None
        if rec.media_entries:
            for m in rec.media_entries:
                if m.thumbnail_path:
                    first_thumb = f"/api/media/{m.id}/thumbnail"
                    break

        preview = None
        if rec.text_entries:
            preview = rec.text_entries[0].content[:100]

        item = RecordListItem(
            date=rec.date,
            media_count=len(rec.media_entries),
            text_count=len(rec.text_entries),
            first_thumbnail=first_thumb,
            use_default_media_placeholder=rec.use_default_media_placeholder,
            has_milestone=rec.milestone is not None,
            milestone_name=rec.milestone.name if rec.milestone else None,
            milestone_icon=(
                rec.milestone.category.icon
                if rec.milestone and rec.milestone.category
                else None
            ),
            preview_text=preview,
        )
        items.append(item)

    return RecordListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{date}", response_model=RecordResponse)
async def get_record(
    date: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """按日期获取某天的完整记录，包含媒体列表、文字列表、里程碑和生长指标。"""
    result = await db.execute(
        select(DailyRecord)
        .where(
            DailyRecord.date == date,
            DailyRecord.user_id == current_user.id,
        )
        .options(
            selectinload(DailyRecord.media_entries),
            selectinload(DailyRecord.text_entries),
            selectinload(DailyRecord.milestone).selectinload(Milestone.category),
            selectinload(DailyRecord.growth_metrics),
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return _build_record_response(record)


@router.post("/", response_model=RecordResponse, status_code=201)
async def create_record(
    data: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新的每日记录（同一用户同一日期只能有一条，重复返回 409）。"""
    existing = await db.execute(
        select(DailyRecord).where(
            DailyRecord.date == data.date,
            DailyRecord.user_id == current_user.id,
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Record already exists for this date")

    record = DailyRecord(
        date=data.date,
        user_id=current_user.id,
        use_default_media_placeholder=data.use_default_media_placeholder,
    )
    db.add(record)
    await db.flush()

    for text_input in data.texts:
        entry = TextEntry(
            daily_record_id=record.id,
            content=text_input.content,
            sort_order=text_input.sort_order,
        )
        db.add(entry)

    await db.commit()

    result = await db.execute(
        select(DailyRecord)
        .options(
            selectinload(DailyRecord.media_entries),
            selectinload(DailyRecord.text_entries),
            selectinload(DailyRecord.milestone).selectinload(Milestone.category),
            selectinload(DailyRecord.growth_metrics),
        )
        .where(DailyRecord.id == record.id)
    )
    record = result.scalars().first()
    return _build_record_response(record)


@router.put("/{date}", response_model=RecordResponse)
async def update_record(
    date: str,
    data: RecordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新指定日期的记录，采用全量替换策略更新文字列表：不在请求体中的旧条目将被删除。"""
    result = await db.execute(
        select(DailyRecord)
        .options(selectinload(DailyRecord.text_entries))
        .where(
            DailyRecord.date == date,
            DailyRecord.user_id == current_user.id,
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    existing_ids = {e.id for e in record.text_entries}
    incoming_ids = {t.id for t in data.texts if t.id is not None}

    for entry in record.text_entries:
        if entry.id not in incoming_ids:
            await db.delete(entry)

    for text_input in data.texts:
        if text_input.id and text_input.id in existing_ids:
            res = await db.execute(
                select(TextEntry).where(TextEntry.id == text_input.id)
            )
            entry = res.scalars().first()
            if entry:
                entry.content = text_input.content
                entry.sort_order = text_input.sort_order
        else:
            db.add(
                TextEntry(
                    daily_record_id=record.id,
                    content=text_input.content,
                    sort_order=text_input.sort_order,
                )
            )

    if data.use_default_media_placeholder is not None:
        record.use_default_media_placeholder = data.use_default_media_placeholder

    await db.commit()

    result = await db.execute(
        select(DailyRecord)
        .options(
            selectinload(DailyRecord.media_entries),
            selectinload(DailyRecord.text_entries),
            selectinload(DailyRecord.milestone).selectinload(Milestone.category),
            selectinload(DailyRecord.growth_metrics),
        )
        .where(DailyRecord.id == record.id)
    )
    record = result.scalars().first()
    return _build_record_response(record)


@router.delete("/{date}", status_code=204)
async def delete_record(
    date: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除指定日期的记录，同时清理该记录关联的所有媒体文件（原图和缩略图）。"""
    result = await db.execute(
        select(DailyRecord)
        .options(selectinload(DailyRecord.media_entries))
        .where(
            DailyRecord.date == date,
            DailyRecord.user_id == current_user.id,
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    for media in record.media_entries:
        cleanup_media_files(media.original_path, media.thumbnail_path)

    await db.delete(record)
    await db.commit()


def _build_record_response(record) -> RecordResponse:
    """将 ORM 对象（含关联子对象）组装为 RecordResponse 响应体。"""
    milestone_info = None
    if record.milestone:
        milestone_info = MilestoneInfo(
            id=record.milestone.id,
            name=record.milestone.name,
            description=record.milestone.description,
            category_id=record.milestone.category_id,
            category_name=(
                record.milestone.category.name if record.milestone.category else None
            ),
            category_icon=(
                record.milestone.category.icon if record.milestone.category else None
            ),
        )

    return RecordResponse(
        id=record.id,
        date=record.date,
        created_at=record.created_at,
        updated_at=record.updated_at,
        use_default_media_placeholder=record.use_default_media_placeholder,
        media_entries=[MediaEntryResponse.model_validate(m) for m in record.media_entries],
        text_entries=[TextEntryResponse.model_validate(t) for t in record.text_entries],
        milestone=milestone_info,
        growth_metrics=[
            GrowthMetricResponse.model_validate(g) for g in record.growth_metrics
        ],
    )
