from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import (
    ALLOWED_IMAGE_TYPES,
    ALLOWED_MEDIA_TYPES,
    ALLOWED_VIDEO_TYPES,
    MAX_VIDEO_SIZE,
    THUMBNAIL_MAX_SIZE,
    THUMBNAIL_QUALITY,
)
from app.database.connection import async_session
from app.models.daily_record import DailyRecord
from app.models.media_entry import MediaEntry
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


async def get_db():
    async with async_session() as session:
        yield session


@router.post("/upload", response_model=MediaUploadResponse, status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    daily_record_id: int = Form(...),
    description: Optional[str] = Form(None),
    sort_order: int = Form(0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyRecord).where(DailyRecord.id == daily_record_id)
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="Daily record not found")

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
    await db.commit()
    await db.refresh(entry)
    return MediaUploadResponse.model_validate(entry)


@router.get("/{media_id}/file")
async def serve_file(media_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MediaEntry).where(MediaEntry.id == media_id))
    entry = result.scalars().first()
    if not entry:
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

    def _iter_file():
        with open(full_path, "rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(
        _iter_file(),
        media_type=content_type,
        headers={
            "Content-Disposition": (
                f'inline; filename="{entry.original_filename or full_path.name}"'
            )
        },
    )


@router.get("/{media_id}/thumbnail")
async def serve_thumbnail(media_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MediaEntry).where(MediaEntry.id == media_id))
    entry = result.scalars().first()
    if not entry or not entry.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    full_path = resolve_thumbnail_path(entry.thumbnail_path)
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found on disk")

    return FileResponse(full_path, media_type="image/jpeg")


@router.put("/{media_id}", response_model=MediaUploadResponse)
async def update_media(
    media_id: int, data: MediaUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(MediaEntry).where(MediaEntry.id == media_id))
    entry = result.scalars().first()
    if not entry:
        raise HTTPException(status_code=404, detail="Media not found")

    if data.description is not None:
        entry.description = data.description
    if data.sort_order is not None:
        entry.sort_order = data.sort_order

    await db.commit()
    await db.refresh(entry)
    return MediaUploadResponse.model_validate(entry)


@router.delete("/{media_id}", status_code=204)
async def delete_media(media_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MediaEntry).where(MediaEntry.id == media_id))
    entry = result.scalars().first()
    if not entry:
        raise HTTPException(status_code=404, detail="Media not found")

    cleanup_media_files(entry.original_path, entry.thumbnail_path)
    await db.delete(entry)
    await db.commit()
