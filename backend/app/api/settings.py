import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.app_settings import AppSettings
from app.models.user import User
from app.schemas.settings import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def _parse_value(key: str, raw: str):
    """将数据库中存储的字符串值转换为对应的 Python 类型（布尔/整数/字符串）。"""
    if key == "dark_mode":
        return raw.lower() in ("true", "1", "yes")
    if key in ("thumbnail_max_size", "thumbnail_quality"):
        try:
            return int(raw)
        except ValueError:
            return raw
    return raw


def _serialize_value(value) -> str:
    """将 Python 值序列化为数据库可存储的字符串（布尔值转为 'true'/'false'）。"""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    _current: User = Depends(get_current_user),
):
    """读取所有应用设置项并按类型解析后返回（需登录鉴权）。"""
    result = await db.execute(select(AppSettings))
    rows = result.scalars().all()
    data = {row.key: _parse_value(row.key, row.value) for row in rows}
    return SettingsResponse(**data)


@router.put("/", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    _current: User = Depends(get_current_user),
):
    """批量更新设置项（仅更新请求体中非 None 的字段），更新后返回全量最新设置。"""
    updates = data.model_dump(exclude_none=True)
    for key, value in updates.items():
        serialized = _serialize_value(value)
        result = await db.execute(select(AppSettings).where(AppSettings.key == key))
        setting = result.scalars().first()
        if setting:
            setting.value = serialized
        else:
            db.add(AppSettings(key=key, value=serialized))

    await db.commit()

    result = await db.execute(select(AppSettings))
    rows = result.scalars().all()
    all_data = {row.key: _parse_value(row.key, row.value) for row in rows}
    return SettingsResponse(**all_data)
