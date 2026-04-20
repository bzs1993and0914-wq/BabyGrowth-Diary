from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import async_session
from app.models.user import User
from app.services.auth_service import user_id_from_media_token, user_id_from_token

security = HTTPBearer(auto_error=True)
security_optional = HTTPBearer(auto_error=False)


async def get_db():
    """FastAPI 依赖项：提供一个请求级别的异步数据库会话，请求结束后自动关闭。"""
    async with async_session() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI 依赖项：校验 Bearer Token 并返回当前登录用户。

    解析 JWT 获取 user_id，再查库确认用户存在；任何一步失败均返回 401。
    """
    user_id = user_id_from_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="登录已过期或无效")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期或无效")
    return user


async def get_current_user_flexible(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI 依赖项：媒体端点专用的双通道鉴权。

    - `Authorization: Bearer <full-scope JWT>`：用于 JS 侧通过 axios 发起的请求；
    - `?token=<media-scope JWT>`：用于 ``<img>/<video>`` 标签直接加载，仅接受
      由 ``POST /api/auth/media-token`` 颁发的短时效 media scope token，
      避免完整登录 JWT 随 URL 流转到日志/浏览历史/右键复制链接等通道中。
    """
    user_id: Optional[int] = None
    if credentials:
        user_id = user_id_from_token(credentials.credentials)
    elif token:
        user_id = user_id_from_media_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="登录已过期或无效")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期或无效")
    return user
