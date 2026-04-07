"""SQLite column upgrades for existing installs (before full Alembic)."""

from __future__ import annotations

from sqlalchemy import inspect, text


def upgrade_schema_sync(conn) -> None:
    """检测旧版数据库是否缺少新字段，若缺失则通过 ALTER TABLE 补全。

    在引入 Alembic 迁移之前，此函数承担 schema 兼容升级的职责，
    保证既有安装在升级后能正常运行，无需手动执行 SQL。
    """
    inspector = inspect(conn)
    tables = inspector.get_table_names()

    if "daily_records" in tables:
        cols = {c["name"] for c in inspector.get_columns("daily_records")}
        if "user_id" not in cols:
            conn.execute(text("ALTER TABLE daily_records ADD COLUMN user_id INTEGER"))
        if "use_default_media_placeholder" not in cols:
            conn.execute(
                text(
                    "ALTER TABLE daily_records ADD COLUMN use_default_media_placeholder "
                    "INTEGER NOT NULL DEFAULT 0"
                )
            )
        if "allergy_notes" not in cols:
            conn.execute(text("ALTER TABLE daily_records ADD COLUMN allergy_notes TEXT"))
