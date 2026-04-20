# Data Model: 004-parent-words-module

## 新增表: `parent_words`

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | `INTEGER` | PK, AUTOINCREMENT | 主键 |
| `user_id` | `INTEGER` | FK → `users.id`, NOT NULL | 所属用户 |
| `title` | `TEXT` | NOT NULL | 标题，最长 100 字符（应用层校验） |
| `content` | `TEXT` | NOT NULL | 正文内容，不限长度 |
| `author_role` | `TEXT` | NULLABLE | 作者身份：`dad` / `mom` / `NULL`（`NULL` 表示未标注，显示为"父母"） |
| `created_at` | `TEXT` | NOT NULL, DEFAULT now() | ISO 8601 时间戳 |
| `updated_at` | `TEXT` | NOT NULL, DEFAULT now() | ISO 8601 时间戳，每次更新时刷新 |

**索引**:
- `ix_parent_words_user_id_created` ON `(user_id, created_at DESC)` — 列表查询主索引

**关系**:
- `user` → `User` (many-to-one)
- `media_entries` → `MediaEntry[]` (one-to-many, cascade delete)

**校验（应用层）**:
- `title`：非空，`strip()` 后长度 1–100
- `content`：非空，`strip()` 后长度 ≥ 1
- `author_role`：`None` / `"dad"` / `"mom"` 枚举值

## 扩展表: `media_entries`（新增列）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `parent_word_id` | `INTEGER` | FK → `parent_words.id` ON DELETE CASCADE, NULLABLE | 所属心语记录（与 `daily_record_id` 互斥） |

**互斥规则（应用层）**:
- 每条 `MediaEntry` 的 `daily_record_id` 和 `parent_word_id` 有且仅有一个非 NULL
- 上传时由 API 层校验：请求中必须提供且仅提供一个关联 ID

**影响**:
- `MediaEntry` 模型增加 `parent_word_id` mapped_column + relationship
- `MediaEntry.daily_record_id` 原为 `NOT NULL`，需改为 `NULLABLE`（配合 schema_upgrade 做旧数据兼容）
- 上传/下载/缩略图端点无需修改——通过 `media_entries.id` 访问，鉴权时检查 `parent_word.user_id` 或 `daily_record.user_id`

## 扩展表: `users`（新增列）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `parent_role` | `TEXT` | NULLABLE, DEFAULT NULL | 用户角色：`dad` / `mom` / `NULL`（未设置） |

**影响**:
- `AuthUser` 响应类型新增 `parent_role` 字段
- `/api/auth/me` 自动返回
- 设置页面提供"我的角色"选项更新此字段

## Schema 升级 (`schema_upgrade.py` 新增)

```python
# media_entries 表
if "media_entries" in tables:
    cols = {c["name"] for c in inspector.get_columns("media_entries")}
    if "parent_word_id" not in cols:
        conn.execute(text(
            "ALTER TABLE media_entries ADD COLUMN parent_word_id INTEGER "
            "REFERENCES parent_words(id) ON DELETE CASCADE"
        ))
    # daily_record_id 需允许 NULL（新 media 可能只关联 parent_word）
    # SQLite 不支持 ALTER COLUMN，但新记录插入时 NULL 已被允许
    # 旧数据 daily_record_id 全非空，无需迁移

# users 表
if "users" in tables:
    cols = {c["name"] for c in inspector.get_columns("users")}
    if "parent_role" not in cols:
        conn.execute(text(
            "ALTER TABLE users ADD COLUMN parent_role TEXT"
        ))
```

> 注意：`parent_words` 表由 `Base.metadata.create_all` 自动创建（新表），无需 ALTER。

## 客户端存储: 草稿自动保存

| 键 | 类型 | 说明 |
|----|------|------|
| `pw-draft-new` | `JSON string` | 新建心语的草稿：`{ title, content, authorRole, mediaIds, savedAt }` |
| `pw-draft-{id}` | `JSON string` | 编辑心语 #{id} 的草稿，结构同上 |

存储位置：浏览器 `localStorage`，不进入 SQLite 或 Electron userData。

## ER 关系图（文字版）

```
User ──1:N──> ParentWord ──1:N──> MediaEntry
  │                                    ↑
  └──1:N──> DailyRecord ──1:N─────────┘
```

一条 `MediaEntry` 通过 `daily_record_id` 或 `parent_word_id`（互斥）关联到它的父实体。
