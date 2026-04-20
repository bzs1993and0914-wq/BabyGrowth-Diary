import platform
import secrets
from pathlib import Path

APP_NAME = "BabyGrow"
VERSION = "0.1.0"
PORT = 18900

if platform.system() == "Darwin":
    APP_DATA_DIR = Path.home() / "Library" / "Application Support" / APP_NAME
elif platform.system() == "Windows":
    APP_DATA_DIR = Path(
        __import__("os").environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
    ) / APP_NAME
else:
    APP_DATA_DIR = Path.home() / f".{APP_NAME.lower()}"

DATABASE_PATH = APP_DATA_DIR / "babygrow.db"
MEDIA_BASE_DIR = APP_DATA_DIR / "media"
THUMBNAIL_BASE_DIR = APP_DATA_DIR / "thumbnails"
EXPORT_DIR = APP_DATA_DIR / "exports"

THUMBNAIL_MAX_SIZE = 400
THUMBNAIL_QUALITY = 85

ALLOWED_IMAGE_TYPES = {"jpg", "jpeg", "png", "heic", "heif"}
ALLOWED_VIDEO_TYPES = {"mp4", "mov"}
ALLOWED_MEDIA_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES
MAX_VIDEO_SIZE = 2_147_483_648  # 2GB

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24 * 7

# Max media files per daily record by account tier
TIER_MEDIA_CAP_NORMAL = 1
TIER_MEDIA_CAP_VIP = 9

# 父母心语（parent_words）每条最多可关联的图片数量，前后端需保持一致
PARENT_WORD_MEDIA_CAP = 5

# 媒体访问签名 Token 的默认有效期（秒），用于 <img>/<video> 的查询参数鉴权
MEDIA_TOKEN_TTL_SECONDS = 15 * 60
# 上传文件写盘时的分块大小（字节），避免大视频一次性读入内存
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB


def get_jwt_secret() -> str:
    """Persist a stable secret under app data for JWT signing."""
    path = APP_DATA_DIR / ".jwt_secret"
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    secret = secrets.token_hex(32)
    path.write_text(secret, encoding="utf-8")
    return secret
