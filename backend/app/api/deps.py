from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import async_session
from app.models.user import User
from app.services.auth_service import user_id_from_token

security = HTTPBearer(auto_error=True)


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
