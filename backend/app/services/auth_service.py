from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import jwt

from app.config import (
    JWT_ALGORITHM,
    JWT_EXPIRE_HOURS,
    MEDIA_TOKEN_TTL_SECONDS,
    get_jwt_secret,
)

# JWT 中的 scope 字段用于区分"完整登录 token"和"仅用于媒体 URL 鉴权的短时效 token"。
# 媒体 token 的权限更窄、TTL 更短，即使随 URL 泄漏（日志/历史/右键复制）危害也有限。
SCOPE_FULL = "full"
SCOPE_MEDIA = "media"


def hash_password(plain: str) -> str:
    """使用 bcrypt 对明文密码进行加盐哈希，返回可直接存库的哈希字符串。"""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    """校验明文密码与 bcrypt 哈希是否匹配；哈希格式非法时返回 False。"""
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8"), password_hash.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(user_id: int, username: str) -> str:
    """生成完整登录用 JWT（scope=full），有效期由 JWT_EXPIRE_HOURS 控制。"""
    secret = get_jwt_secret()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "username": username,
        "scope": SCOPE_FULL,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def create_media_access_token(
    user_id: int, ttl_seconds: int = MEDIA_TOKEN_TTL_SECONDS
) -> tuple[str, int]:
    """生成媒体访问专用短时效 token（scope=media），仅可用于媒体文件端点。

    返回 `(token, expires_at_unix_seconds)`，便于前端按 exp 提前刷新。
    """
    secret = get_jwt_secret()
    now = datetime.now(timezone.utc)
    exp = int((now + timedelta(seconds=ttl_seconds)).timestamp())
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "scope": SCOPE_MEDIA,
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM), exp


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """解码并验证 JWT，过期或签名无效时返回 None。"""
    try:
        return jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def user_id_from_token(token: str) -> Optional[int]:
    """从 JWT 中提取 user_id（payload 的 sub 字段）；令牌无效时返回 None。

    兼容老版本没有 scope 字段的 token；但明确是 media scope 的 token 不允许通过
    此函数（仅能访问媒体端点，参见 user_id_from_media_token）。
    """
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    if payload.get("scope") == SCOPE_MEDIA:
        return None
    try:
        return int(payload["sub"])
    except (TypeError, ValueError):
        return None


def user_id_from_media_token(token: str) -> Optional[int]:
    """从 JWT 中提取 user_id，且强制要求 scope=media；否则返回 None。"""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    if payload.get("scope") != SCOPE_MEDIA:
        return None
    try:
        return int(payload["sub"])
    except (TypeError, ValueError):
        return None
