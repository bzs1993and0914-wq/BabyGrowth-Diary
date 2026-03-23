from sqlalchemy import select

from app.database.connection import async_session, engine
from app.models import Base
from app.models.milestone_category import MilestoneCategory
from app.models.app_settings import AppSettings

PRESET_CATEGORIES = [
    {"name": "身体发育", "icon": "Trophy", "is_preset": True},
    {"name": "语言发展", "icon": "ChatDotRound", "is_preset": True},
    {"name": "情感互动", "icon": "Heart", "is_preset": True},
    {"name": "饮食变化", "icon": "Bowl", "is_preset": True},
    {"name": "其他", "icon": "Star", "is_preset": True},
]

DEFAULT_SETTINGS = {
    "theme": "default",
    "dark_mode": "false",
    "thumbnail_max_size": "400",
    "thumbnail_quality": "85",
}


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        result = await session.execute(
            select(MilestoneCategory).where(MilestoneCategory.is_preset.is_(True))
        )
        if not result.scalars().first():
            for cat in PRESET_CATEGORIES:
                session.add(MilestoneCategory(**cat))

        result = await session.execute(select(AppSettings))
        existing_keys = {row.key for row in result.scalars().all()}
        for key, value in DEFAULT_SETTINGS.items():
            if key not in existing_keys:
                session.add(AppSettings(key=key, value=value))

        await session.commit()
