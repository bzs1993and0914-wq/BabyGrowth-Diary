from __future__ import annotations

import uuid
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_user_flexible, get_db
from app.config import (
    ALLOWED_MEDIA_TYPES,
    ALLOWED_VIDEO_TYPES,
    MAX_VIDEO_SIZE,
    THUMBNAIL_MAX_SIZE,
    THUMBNAIL_QUALITY,
    TIER_MEDIA_CAP_NORMAL,
    TIER_MEDIA_CAP_VIP,
)
from app.models.daily_record import DailyRecord
from app.models.media_entry import MediaEntry
from app.models.user import User
from app.schemas.media import MediaUpdate, MediaUploadResponse
from app.services.media_processor import (
    convert_heic_to_jpeg,
    extract_exif_date,
    generate_image_thumbnail,
    generate_video_thumbnail,
)
from app.services.storage_manager import (
    cleanup_media_files,
    get_media_dir,
    get_thumbnail_dir,
    resolve_media_path,
    resolve_thumbnail_path,
)

router = APIRouter(prefix="/media", tags=["media"])


def _tier_cap(tier: str) -> int:
    """根据账号等级返回每条记录允许上传的媒体文件上限数量。"""
    return TIER_MEDIA_CAP_VIP if tier == "vip" else TIER_MEDIA_CAP_NORMAL


@router.post("/upload", response_model=MediaUploadResponse, status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    daily_record_id: int = Form(...),
    description: Optional[str] = Form(None),
    sort_order: int = Form(0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传媒体文件到指定日期记录。

    流程：校验账号媒体上限 → 校验文件类型和大小 → 保存原文件 →
    HEIC 自动转 JPEG → 生成缩略图（图片/视频各自处理） → 提取图片 EXIF 日期 →
    写入数据库记录。
    """
    result = await db.execute(
        select(DailyRecord).where(
            DailyRecord.id == daily_record_id,
            DailyRecord.user_id == current_user.id,
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Daily record not found")

    count_result = await db.execute(
        select(func.count(MediaEntry.id)).where(
            MediaEntry.daily_record_id == daily_record_id
        )
    )
    existing = int(count_result.scalar() or 0)
    cap = _tier_cap(current_user.account_tier)
    if existing >= cap:
        raise HTTPException(
            status_code=400,
            detail=f"已达到当前账号可关联的照片/视频上限（{cap} 个）",
        )

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed: {ALLOWED_MEDIA_TYPES}",
        )

    is_video = ext in ALLOWED_VIDEO_TYPES
    is_heic = ext in {"heic", "heif"}
    media_type = "video" if is_video else "image"

    content = await file.read()
    file_size = len(content)

    if is_video and file_size > MAX_VIDEO_SIZE:
        raise HTTPException(status_code=400, detail="Video file exceeds 2GB limit")

    media_dir = get_media_dir(record.date)
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = media_dir / unique_name
    file_path.write_bytes(content)

    date_parts = record.date.split("-")
    relative_original = f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}/{unique_name}"

    saved_path = file_path
    if is_heic:
        jpeg_name = f"{uuid.uuid4().hex}.jpg"
        jpeg_path = media_dir / jpeg_name
        if convert_heic_to_jpeg(file_path, jpeg_path):
            saved_path = jpeg_path
            relative_original = (
                f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}/{jpeg_name}"
            )

    thumbnail_dir = get_thumbnail_dir(record.date)
    thumb_name = f"{uuid.uuid4().hex}.jpg"
    thumb_path = thumbnail_dir / thumb_name
    relative_thumb: Optional[str] = (
        f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}/{thumb_name}"
    )

    if is_video:
        if not generate_video_thumbnail(saved_path, thumb_path):
            relative_thumb = None
    else:
        if not generate_image_thumbnail(
            saved_path, thumb_path, THUMBNAIL_MAX_SIZE, THUMBNAIL_QUALITY
        ):
            relative_thumb = None

    exif_date = None
    if not is_video:
        exif_date = extract_exif_date(saved_path)

    entry = MediaEntry(
        daily_record_id=daily_record_id,
        media_type=media_type,
        original_path=relative_original,
        thumbnail_path=relative_thumb,
        description=description,
        file_size=file_size,
        original_filename=file.filename,
        exif_date=exif_date,
        sort_order=sort_order,
    )
    db.add(entry)
    if record.use_default_media_placeholder:
        record.use_default_media_placeholder = False
    await db.commit()
    await db.refresh(entry)
    return MediaUploadResponse.model_validate(entry)


@router.get("/{media_id}/file")
async def serve_file(
    media_id: int,
    current_user: User = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
):
    """提供原始媒体文件。使用 FileResponse 以支持 HTTP Range，便于 <video> 拖拽进度条与跳转。"""
    result = await db.execute(select(MediaEntry).where(MediaEntry.id == media_id))
    entry = result.scalars().first()
    if not entry:
        raise HTTPException(status_code=404, detail="Media not found")

    rec_res = await db.execute(
        select(DailyRecord).where(
            DailyRecord.id == entry.daily_record_id,
            DailyRecord.user_id == current_user.id,
        )
    )
    if not rec_res.scalars().first():
        raise HTTPException(status_code=404, detail="Media not found")

    full_path = resolve_media_path(entry.original_path)
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    media_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "mp4": "video/mp4",
        "mov": "video/quicktime",
    }
    ext = full_path.suffix.lstrip(".").lower()
    content_type = media_types.get(ext, "application/octet-stream")
    download_name = entry.original_filename or full_path.name
    safe_fallback = full_path.name.replace("\\", "\\\\").replace('"', '\\"')
    try:
        download_name.encode("latin-1")
        safe_download_name = download_name.replace("\\", "\\\\").replace('"', '\\"')
        content_disposition = f'inline; filename="{safe_download_name}"'
    except UnicodeEncodeError:
        content_disposition = (
            f'inline; filename="{safe_fallback}"; '
            f"filename*=UTF-8''{quote(download_name)}"
        )

    return FileResponse(
        path=full_path,
        media_type=content_type,
        headers={"Content-Disposition": content_disposition},
    )


@router.get("/{media_id}/thumbnail")
async def serve_thumbnail(
    media_id: int,
    current_user: User = Depends(get_current_user_flexible),
    db: AsyncSession = Depends(get_db),
):
    """返回媒体文件对应的缩略图（JPEG 格式），缩略图不存在时返回 404。"""
    result = await db.execute(select(MediaEntry).where(MediaEntry.id == media_id))
    entry = result.scalars().first()
    if not entry or not entry.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    rec_res = await db.execute(
        select(DailyRecord).where(
            DailyRecord.id == entry.daily_record_id,
            DailyRecord.user_id == current_user.id,
        )
    )
    if not rec_res.scalars().first():
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    full_path = resolve_thumbnail_path(entry.thumbnail_path)
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found on disk")

    return FileResponse(full_path, media_type="image/jpeg")


@router.put("/{media_id}", response_model=MediaUploadResponse)
async def update_media(
    media_id: int,
    data: MediaUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新媒体文件的描述文字或排列顺序（不更换文件本身）。"""
    result = await db.execute(select(MediaEntry).where(MediaEntry.id == media_id))
    entry = result.scalars().first()
    if not entry:
        raise HTTPException(status_code=404, detail="Media not found")

    rec_res = await db.execute(
        select(DailyRecord).where(
            DailyRecord.id == entry.daily_record_id,
            DailyRecord.user_id == current_user.id,
        )
    )
    if not rec_res.scalars().first():
        raise HTTPException(status_code=404, detail="Media not found")

    if data.description is not None:
        entry.description = data.description
    if data.sort_order is not None:
        entry.sort_order = data.sort_order

    await db.commit()
    await db.refresh(entry)
    return MediaUploadResponse.model_validate(entry)


@router.delete("/{media_id}", status_code=204)
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除媒体记录，同时从磁盘删除原文件和缩略图。"""
    result = await db.execute(select(MediaEntry).where(MediaEntry.id == media_id))
    entry = result.scalars().first()
    if not entry:
        raise HTTPException(status_code=404, detail="Media not found")

    rec_res = await db.execute(
        select(DailyRecord).where(
            DailyRecord.id == entry.daily_record_id,
            DailyRecord.user_id == current_user.id,
        )
    )
    if not rec_res.scalars().first():
        raise HTTPException(status_code=404, detail="Media not found")

    cleanup_media_files(entry.original_path, entry.thumbnail_path)
    await db.delete(entry)
    await db.commit()
