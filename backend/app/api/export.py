from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import async_session
from app.models.daily_record import DailyRecord
from app.models.media_entry import MediaEntry
from app.schemas.export import ExportRequest, ExportStatus, StorageStats
from app.services.export_service import get_export_status, start_export
from app.services.storage_manager import get_storage_stats

router = APIRouter(tags=["export"])


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/export", response_model=ExportStatus, status_code=202)
async def create_export(data: ExportRequest):
    export_id = await start_export(data.date_from, data.date_to)
    return ExportStatus(export_id=export_id, status="processing", progress=0.0)


@router.get("/export/status", response_model=ExportStatus)
async def check_export_status(export_id: str = Query(...)):
    status = get_export_status(export_id)
    if not status:
        raise HTTPException(status_code=404, detail="Export not found")
    return ExportStatus(**status)


@router.get("/storage/stats", response_model=StorageStats)
async def storage_stats(db: AsyncSession = Depends(get_db)):
    record_count = await db.execute(select(func.count(DailyRecord.id)))
    total_records = record_count.scalar() or 0

    media_count = await db.execute(select(func.count(MediaEntry.id)))
    total_media = media_count.scalar() or 0

    image_count = await db.execute(
        select(func.count(MediaEntry.id)).where(MediaEntry.media_type == "image")
    )
    total_images = image_count.scalar() or 0

    video_count = await db.execute(
        select(func.count(MediaEntry.id)).where(MediaEntry.media_type == "video")
    )
    total_videos = video_count.scalar() or 0

    disk_stats = get_storage_stats()

    return StorageStats(
        total_records=total_records,
        total_media=total_media,
        total_images=total_images,
        total_videos=total_videos,
        **disk_stats,
    )
