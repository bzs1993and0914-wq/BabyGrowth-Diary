from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

from app.config import APP_DATA_DIR, DATABASE_PATH, MEDIA_BASE_DIR, THUMBNAIL_BASE_DIR

logger = logging.getLogger(__name__)


def get_media_dir(date: str, subfolder: Optional[str] = None) -> Path:
    """Returns and creates media/{subfolder?}/{YYYY}/{MM}/{DD}/ directory."""
    parts = date.split("-")
    path = MEDIA_BASE_DIR
    if subfolder:
        path = path / subfolder
    path = path / parts[0] / parts[1] / parts[2]
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_thumbnail_dir(date: str, subfolder: Optional[str] = None) -> Path:
    """Returns and creates thumbnails/{subfolder?}/{YYYY}/{MM}/{DD}/ directory."""
    parts = date.split("-")
    path = THUMBNAIL_BASE_DIR
    if subfolder:
        path = path / subfolder
    path = path / parts[0] / parts[1] / parts[2]
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_media_path(relative_path: str) -> Path:
    """将数据库中存储的相对路径还原为媒体文件的绝对路径。"""
    return MEDIA_BASE_DIR / relative_path


def resolve_thumbnail_path(relative_path: str) -> Path:
    """将数据库中存储的相对路径还原为缩略图的绝对路径。"""
    return THUMBNAIL_BASE_DIR / relative_path


def get_storage_stats() -> Dict[str, int]:
    """统计媒体目录、缩略图目录和数据库文件各自占用的磁盘字节数。"""
    media_size = _dir_size(MEDIA_BASE_DIR)
    thumbnail_size = _dir_size(THUMBNAIL_BASE_DIR)
    db_size = DATABASE_PATH.stat().st_size if DATABASE_PATH.exists() else 0
    return {
        "media_size_bytes": media_size,
        "thumbnail_size_bytes": thumbnail_size,
        "database_size_bytes": db_size,
        "total_size_bytes": media_size + thumbnail_size + db_size,
    }


def cleanup_media_files(
    original_path: Optional[str], thumbnail_path: Optional[str]
) -> None:
    """删除原始媒体文件和缩略图，路径为 None 或文件不存在时静默跳过。"""
    for rel_path, resolver in [
        (original_path, resolve_media_path),
        (thumbnail_path, resolve_thumbnail_path),
    ]:
        if rel_path:
            full = resolver(rel_path)
            try:
                if full.exists():
                    full.unlink()
            except Exception:
                logger.exception("Failed to delete file: %s", full)


def ensure_dirs() -> None:
    """应用启动时确保所有必要目录（应用数据、媒体、缩略图）已创建。"""
    for d in (APP_DATA_DIR, MEDIA_BASE_DIR, THUMBNAIL_BASE_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _dir_size(path: Path) -> int:
    """递归统计目录下所有文件的总字节数，目录不存在时返回 0。"""
    if not path.exists():
        return 0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
