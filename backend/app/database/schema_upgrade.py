"""SQLite column upgrades for existing installs (before full Alembic)."""

from __future__ import annotations

import logging

from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)


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

    if "media_entries" in tables:
        cols = {c["name"] for c in inspector.get_columns("media_entries")}
        if "parent_word_id" not in cols:
            conn.execute(
                text(
                    "ALTER TABLE media_entries ADD COLUMN parent_word_id INTEGER "
                    "REFERENCES parent_words(id) ON DELETE CASCADE"
                )
            )

        col_map = {c["name"]: c for c in inspector.get_columns("media_entries")}
        if not col_map.get("daily_record_id", {}).get("nullable", True):
            _rebuild_media_entries_nullable(conn)

    if "users" in tables:
        cols = {c["name"] for c in inspector.get_columns("users")}
        if "parent_role" not in cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN parent_role TEXT"))

    if "parent_word_highlights" not in tables:
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS parent_word_highlights ("
                "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "  parent_word_id INTEGER NOT NULL REFERENCES parent_words(id) ON DELETE CASCADE,"
                "  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,"
                "  start_offset INTEGER NOT NULL,"
                "  end_offset INTEGER NOT NULL,"
                "  color TEXT DEFAULT 'yellow',"
                "  created_at TEXT NOT NULL DEFAULT (datetime('now'))"
                ")"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_pwh_parent_word_id "
                "ON parent_word_highlights(parent_word_id)"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_pwh_user_id "
                "ON parent_word_highlights(user_id)"
            )
        )


def _rebuild_media_entries_nullable(conn) -> None:
    """Rebuild media_entries to make daily_record_id nullable.

    SQLite does not support ALTER COLUMN, so we recreate the table.
    迁移过程中必须保留 CHECK 约束和索引，否则旧库升级后会丢失数据完整性保障。
    """
    logger.info("Migrating media_entries: daily_record_id NOT NULL → nullable")

    existing_indexes = {
        row[1]
        for row in conn.execute(
            text(
                "SELECT * FROM sqlite_master "
                "WHERE type='index' AND tbl_name='media_entries'"
            )
        ).fetchall()
    }

    conn.execute(text("PRAGMA foreign_keys = OFF"))
    conn.execute(
        text(
            "CREATE TABLE media_entries_new ("
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "  daily_record_id INTEGER REFERENCES daily_records(id) ON DELETE CASCADE,"
            "  parent_word_id INTEGER REFERENCES parent_words(id) ON DELETE CASCADE,"
            "  media_type VARCHAR(10) NOT NULL,"
            "  original_path TEXT NOT NULL,"
            "  thumbnail_path TEXT,"
            "  description TEXT,"
            "  file_size INTEGER,"
            "  original_filename TEXT,"
            "  exif_date TEXT,"
            "  sort_order INTEGER NOT NULL DEFAULT 0,"
            "  created_at TEXT NOT NULL,"
            "  CONSTRAINT ck_media_type CHECK (media_type IN ('image', 'video'))"
            ")"
        )
    )
    conn.execute(
        text(
            "INSERT INTO media_entries_new "
            "  (id, daily_record_id, parent_word_id, media_type, original_path,"
            "   thumbnail_path, description, file_size, original_filename,"
            "   exif_date, sort_order, created_at) "
            "SELECT id, daily_record_id, parent_word_id, media_type, original_path,"
            "   thumbnail_path, description, file_size, original_filename,"
            "   exif_date, sort_order, created_at "
            "FROM media_entries"
        )
    )
    conn.execute(text("DROP TABLE media_entries"))
    conn.execute(text("ALTER TABLE media_entries_new RENAME TO media_entries"))

    conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_media_entries_daily_record_id "
            "ON media_entries(daily_record_id)"
        )
    )
    conn.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_media_entries_parent_word_id "
            "ON media_entries(parent_word_id)"
        )
    )

    conn.execute(text("PRAGMA foreign_keys = ON"))
    logger.info(
        "media_entries migration complete (old indexes=%s, ck_media_type restored)",
        sorted(existing_indexes),
    )
