import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import async_session
from app.models.app_settings import AppSettings
from app.schemas.settings import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


async def get_db():
    async with async_session() as session:
        yield session


def _parse_value(key: str, raw: str):
    if key == "dark_mode":
        return raw.lower() in ("true", "1", "yes")
    if key in ("thumbnail_max_size", "thumbnail_quality"):
        try:
            return int(raw)
        except ValueError:
            return raw
    return raw


def _serialize_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


@router.get("/", response_model=SettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppSettings))
    rows = result.scalars().all()
    data = {row.key: _parse_value(row.key, row.value) for row in rows}
    return SettingsResponse(**data)


@router.put("/", response_model=SettingsResponse)
async def update_settings(data: SettingsUpdate, db: AsyncSession = Depends(get_db)):
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
