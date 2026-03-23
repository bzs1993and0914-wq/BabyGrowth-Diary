from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

from app.config import APP_DATA_DIR, DATABASE_PATH, MEDIA_BASE_DIR, THUMBNAIL_BASE_DIR

logger = logging.getLogger(__name__)


def get_media_dir(date: str) -> Path:
    """Returns and creates media/{YYYY}/{MM}/{DD}/ directory."""
    parts = date.split("-")
    path = MEDIA_BASE_DIR / parts[0] / parts[1] / parts[2]
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_thumbnail_dir(date: str) -> Path:
    """Returns and creates thumbnails/{YYYY}/{MM}/{DD}/ directory."""
    parts = date.split("-")
    path = THUMBNAIL_BASE_DIR / parts[0] / parts[1] / parts[2]
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_media_path(relative_path: str) -> Path:
    return MEDIA_BASE_DIR / relative_path


def resolve_thumbnail_path(relative_path: str) -> Path:
    return THUMBNAIL_BASE_DIR / relative_path


def get_storage_stats() -> Dict[str, int]:
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
    for d in (APP_DATA_DIR, MEDIA_BASE_DIR, THUMBNAIL_BASE_DIR):
        d.mkdir(parents=True, exist_ok=True)


def _dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
