# Data Model: 宝宝成长记录桌面应用

**Branch**: `001-baby-growth-timeline` | **Date**: 2026-03-21

## Entity Relationship Diagram

```mermaid
erDiagram
    daily_records ||--o{ media_entries : contains
    daily_records ||--o{ text_entries : contains
    daily_records ||--o| milestones : "may have"
    daily_records ||--o{ growth_metrics : "may have"
    milestones }o--|| milestone_categories : "belongs to"

    daily_records {
        int id PK
        text date UK "YYYY-MM-DD"
        text created_at
        text updated_at
    }

    media_entries {
        int id PK
        int daily_record_id FK
        text media_type "image | video"
        text original_path
        text thumbnail_path
        text description
        int file_size
        text original_filename
        text exif_date
        int sort_order
        text created_at
    }

    text_entries {
        int id PK
        int daily_record_id FK
        text content
        int sort_order
        text created_at
    }

    milestones {
        int id PK
        int daily_record_id FK_UK
        int category_id FK
        text name
        text description
        text created_at
    }

    milestone_categories {
        int id PK
        text name UK
        text icon
        int is_preset
    }

    app_settings {
        text key PK
        text value
    }
```

## Table Definitions

### daily_records

以日期为最小存储单位的记录容器。每个日期唯一对应一条记录。

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| date | TEXT | NOT NULL, UNIQUE | 记录日期 (YYYY-MM-DD) |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |
| updated_at | TEXT | NOT NULL | 最后更新时间 (ISO 8601) |

### media_entries

单个媒体文件（图片或视频）的引用记录。数据库仅存储路径和元数据，实际文件存储在本地文件系统中。

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| daily_record_id | INTEGER | NOT NULL, FK → daily_records.id ON DELETE CASCADE | 所属日期记录 |
| media_type | TEXT | NOT NULL, CHECK IN ('image', 'video') | 媒体类型 |
| original_path | TEXT | NOT NULL | 原始文件相对路径 |
| thumbnail_path | TEXT | | 缩略图相对路径 |
| description | TEXT | | 配文/描述 |
| file_size | INTEGER | | 文件大小 (bytes) |
| original_filename | TEXT | | 原始文件名 |
| exif_date | TEXT | | EXIF 拍摄时间 |
| sort_order | INTEGER | NOT NULL, DEFAULT 0 | 排序序号 |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |

### text_entries

纯文字记录。属于某个日期记录，可以独立于媒体文件存在。

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| daily_record_id | INTEGER | NOT NULL, FK → daily_records.id ON DELETE CASCADE | 所属日期记录 |
| content | TEXT | NOT NULL | 文字内容 |
| sort_order | INTEGER | NOT NULL, DEFAULT 0 | 排序序号 |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |

### milestones

里程碑标记。每个日期最多关联一个里程碑。

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| daily_record_id | INTEGER | NOT NULL, UNIQUE, FK → daily_records.id ON DELETE CASCADE | 所属日期记录 (一对一) |
| category_id | INTEGER | NOT NULL, FK → milestone_categories.id | 所属分类 |
| name | TEXT | NOT NULL | 里程碑名称 (如 "第一次翻身") |
| description | TEXT | | 详细描述 |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |

### milestone_categories

里程碑分类。包含系统预设分类和用户自定义分类。

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| name | TEXT | NOT NULL, UNIQUE | 分类名称 |
| icon | TEXT | | 图标标识 (Element Plus icon name) |
| is_preset | INTEGER | NOT NULL, DEFAULT 0 | 是否预设 (1=预设, 0=自定义) |

### growth_metrics

宝宝的可量化成长指标（身高、体重、头围等），用于绘制成长曲线。

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| daily_record_id | INTEGER | NOT NULL, FK → daily_records.id ON DELETE CASCADE | 所属日期记录 |
| metric_type | TEXT | NOT NULL, CHECK IN ('height', 'weight', 'head_circumference') | 指标类型 |
| value | REAL | NOT NULL | 数值 |
| unit | TEXT | NOT NULL | 单位 (cm, kg) |
| created_at | TEXT | NOT NULL | 创建时间 (ISO 8601) |

### app_settings

应用级键值对设置。

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| key | TEXT | PRIMARY KEY | 设置键名 |
| value | TEXT | NOT NULL | 设置值 (JSON 序列化) |

## Indexes

| Index Name | Table | Columns | Purpose |
|------------|-------|---------|---------|
| idx_daily_records_date | daily_records | date | 按日期快速查询记录 |
| idx_media_entries_record | media_entries | daily_record_id | 按日期记录查询媒体条目 |
| idx_text_entries_record | text_entries | daily_record_id | 按日期记录查询文字条目 |
| idx_milestones_category | milestones | category_id | 按分类筛选里程碑 |
| idx_growth_metrics_record | growth_metrics | daily_record_id | 按日期记录查询成长指标 |
| idx_growth_metrics_type | growth_metrics | metric_type | 按指标类型查询（绘制曲线） |

## Preset Data

### milestone_categories 预设分类

| id | name | icon | is_preset |
|----|------|------|-----------|
| 1 | 身体发育 | Trophy | 1 |
| 2 | 语言发展 | ChatDotRound | 1 |
| 3 | 情感互动 | Heart | 1 |
| 4 | 饮食变化 | Bowl | 1 |
| 5 | 其他 | Star | 1 |

### app_settings 默认值

| key | value |
|-----|-------|
| theme | "default" |
| dark_mode | "false" |
| thumbnail_max_size | "400" |
| thumbnail_quality | "85" |

## File Storage Layout

媒体文件按日期分层存储在应用数据目录中，与数据库解耦：

```text
{APP_DATA_DIR}/
├── babygrow.db                    # SQLite 数据库文件
├── media/                         # 原始媒体文件
│   └── YYYY/
│       └── MM/
│           └── DD/
│               ├── {uuid}.jpg
│               ├── {uuid}.png
│               └── {uuid}.mp4
└── thumbnails/                    # 缩略图 (可重建)
    └── YYYY/
        └── MM/
            └── DD/
                ├── {uuid}_thumb.jpg
                └── {uuid}_thumb.jpg   # 视频封面
```

- `APP_DATA_DIR` 路径:
  - macOS: `~/Library/Application Support/BabyGrow/`
  - Windows: `%APPDATA%/BabyGrow/`
- 数据库中 `original_path` / `thumbnail_path` 存储相对于 `media/` / `thumbnails/` 的路径
- 缩略图为派生数据，可从原始文件重新生成

## Validation Rules

- `daily_records.date` 格式必须为 `YYYY-MM-DD`，且不能是未来日期
- `media_entries.media_type` 仅允许 `'image'` 或 `'video'`
- `media_entries.file_size` 对于视频类型不得超过 2,147,483,648 bytes (2GB)
- `media_entries.original_path` 引用的文件必须存在，否则 UI 显示占位符
- `text_entries.content` 不允许为空字符串
- `milestone_categories` 预设记录 (`is_preset=1`) 不允许删除
- `milestones.daily_record_id` 唯一约束确保每天最多一个里程碑

## SQLAlchemy Model Example

```python
# backend/app/models/daily_record.py
from sqlalchemy import Column, Integer, Text, event
from sqlalchemy.orm import relationship
from app.database.connection import Base

class DailyRecord(Base):
    __tablename__ = "daily_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Text, nullable=False, unique=True, index=True)
    created_at = Column(Text, nullable=False)
    updated_at = Column(Text, nullable=False)

    media_entries = relationship("MediaEntry", back_populates="daily_record", cascade="all, delete-orphan")
    text_entries = relationship("TextEntry", back_populates="daily_record", cascade="all, delete-orphan")
    milestone = relationship("Milestone", back_populates="daily_record", uselist=False, cascade="all, delete-orphan")
```
