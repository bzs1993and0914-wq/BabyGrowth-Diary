from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    MediaTokenResponse,
    MessageResponse,
    ProfileUpdate,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from app.services.auth_service import (
    create_access_token,
    create_media_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_AUTH_INVALID = "用户名或密码错误"


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户并返回 JWT Token。

    若用户名已存在返回 409。首位注册用户会自动认领所有 user_id 为 NULL 的旧记录，
    以支持从无账号模式平滑迁移。
    """
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="该用户名不可用")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        account_tier="normal",
    )
    db.add(user)
    await db.flush()

    count_users = await db.execute(select(func.count(User.id)))
    if (count_users.scalar() or 0) == 1:
        await db.execute(
            text("UPDATE daily_records SET user_id = :uid WHERE user_id IS NULL"),
            {"uid": user.id},
        )

    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id, user.username)
    return TokenResponse(
        access_token=token,
        user=UserPublic.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户名密码登录，校验通过后返回 JWT Token；用户名或密码错误统一返回 401。"""
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalars().first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail=_AUTH_INVALID)

    token = create_access_token(user.id, user.username)
    return TokenResponse(
        access_token=token,
        user=UserPublic.model_validate(user),
    )


@router.get("/me", response_model=UserPublic)
async def me(current: User = Depends(get_current_user)):
    """返回当前登录用户的基本信息（用于前端初始化和刷新用户状态）。"""
    return UserPublic.model_validate(current)


@router.put("/profile", response_model=UserPublic)
async def update_profile(
    data: ProfileUpdate,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.parent_role is not None:
        current.parent_role = data.parent_role
    await db.commit()
    await db.refresh(current)
    return UserPublic.model_validate(current)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改当前用户密码，需先验证旧密码，验证失败返回 401。"""
    if not verify_password(data.current_password, current.password_hash):
        raise HTTPException(status_code=401, detail=_AUTH_INVALID)

    current.password_hash = hash_password(data.new_password)
    await db.commit()
    return MessageResponse(message="密码已更新")


@router.post("/media-token", response_model=MediaTokenResponse)
async def issue_media_token(current: User = Depends(get_current_user)):
    """颁发短时效 (scope=media) token，供前端在 ``<img>/<video>`` URL 查询参数中使用。

    调用方必须先用完整登录 JWT 通过 ``Authorization`` header 鉴权；颁发的 media token
    不能反过来访问任何非媒体端点，降低 URL 泄漏风险。前端应在 token 过期前自行刷新。
    """
    token, expires_at = create_media_access_token(current.id)
    return MediaTokenResponse(token=token, expires_at=expires_at)


@router.post("/dev/set-tier", response_model=UserPublic)
async def dev_set_tier(
    tier: str = Query(..., pattern="^(normal|vip)$"),
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle VIP for manual testing (local desktop app)."""
    current.account_tier = tier
    await db.commit()
    await db.refresh(current)
    return UserPublic.model_validate(current)
