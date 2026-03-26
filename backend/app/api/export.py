from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.daily_record import DailyRecord
from app.models.media_entry import MediaEntry
from app.models.user import User
from app.schemas.export import ExportRequest, ExportStatus, StorageStats
from app.services.export_service import get_export_status, start_export
from app.services.storage_manager import get_storage_stats

router = APIRouter(tags=["export"])


@router.post("/export", response_model=ExportStatus, status_code=202)
async def create_export(
    data: ExportRequest,
    current_user: User = Depends(get_current_user),
):
    """触发异步导出任务（立即返回 202 和 export_id），实际打包在后台进行。"""
    export_id = await start_export(data.date_from, data.date_to, current_user.id)
    return ExportStatus(export_id=export_id, status="processing", progress=0.0)


@router.get("/export/status", response_model=ExportStatus)
async def check_export_status(
    export_id: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    """轮询导出任务状态，返回进度百分比和最终文件路径（完成后）。"""
    status = get_export_status(export_id)
    if not status:
        raise HTTPException(status_code=404, detail="Export not found")
    return ExportStatus(**status)


@router.get("/storage/stats", response_model=StorageStats)
async def storage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """返回当前用户的存储使用统计：记录数、媒体文件数量及磁盘占用字节数。"""
    record_count = await db.execute(
        select(func.count(DailyRecord.id)).where(DailyRecord.user_id == current_user.id)
    )
    total_records = record_count.scalar() or 0

    uid = current_user.id
    media_count = await db.execute(
        select(func.count(MediaEntry.id))
        .select_from(MediaEntry)
        .join(DailyRecord, MediaEntry.daily_record_id == DailyRecord.id)
        .where(DailyRecord.user_id == uid)
    )
    total_media = media_count.scalar() or 0

    image_count = await db.execute(
        select(func.count(MediaEntry.id))
        .select_from(MediaEntry)
        .join(DailyRecord, MediaEntry.daily_record_id == DailyRecord.id)
        .where(
            DailyRecord.user_id == uid,
            MediaEntry.media_type == "image",
        )
    )
    total_images = image_count.scalar() or 0

    video_count = await db.execute(
        select(func.count(MediaEntry.id))
        .select_from(MediaEntry)
        .join(DailyRecord, MediaEntry.daily_record_id == DailyRecord.id)
        .where(
            DailyRecord.user_id == uid,
            MediaEntry.media_type == "video",
        )
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
