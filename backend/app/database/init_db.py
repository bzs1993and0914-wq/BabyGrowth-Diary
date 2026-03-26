from sqlalchemy import func, select, text

from app.database.connection import async_session, engine
from app.database.schema_upgrade import upgrade_schema_sync
from app.models import Base
from app.models.app_settings import AppSettings
from app.models.daily_record import DailyRecord
from app.models.milestone_category import MilestoneCategory
from app.models.user import User
from app.services.auth_service import hash_password

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


async def _ensure_bootstrap_user(session) -> None:
    """若库中无用户但已有记录，自动创建 local/changeme 兜底账号并将旧记录归属给它。

    兼容老版本数据迁移场景：首次引入用户系统时，已存在的 daily_records 的
    user_id 为 NULL，需要关联到一个默认账号才能正常显示。
    """
    n_users = await session.execute(select(func.count(User.id)))
    if (n_users.scalar() or 0) > 0:
        return
    n_recs = await session.execute(select(func.count(DailyRecord.id)))
    if (n_recs.scalar() or 0) == 0:
        return

    user = User(
        username="local",
        password_hash=hash_password("changeme"),
        account_tier="normal",
    )
    session.add(user)
    await session.flush()
    await session.execute(
        text("UPDATE daily_records SET user_id = :uid WHERE user_id IS NULL"),
        {"uid": user.id},
    )


async def init_db() -> None:
    """初始化数据库：建表、执行 Schema 升级、写入预置里程碑分类和默认设置。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(upgrade_schema_sync)

    async with async_session() as session:
        await _ensure_bootstrap_user(session)

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
