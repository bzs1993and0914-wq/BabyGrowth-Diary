from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import jwt

from app.config import JWT_ALGORITHM, JWT_EXPIRE_HOURS, get_jwt_secret


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
    """生成带有用户 ID 和用户名的 JWT，有效期由 JWT_EXPIRE_HOURS 控制。"""
    secret = get_jwt_secret()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "username": username,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """解码并验证 JWT，过期或签名无效时返回 None。"""
    try:
        return jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def user_id_from_token(token: str) -> Optional[int]:
    """从 JWT 中提取 user_id（payload 的 sub 字段）；令牌无效时返回 None。"""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    try:
        return int(payload["sub"])
    except (TypeError, ValueError):
        return None
