# Records API Contract

**Base Path**: `/api/records`

## Endpoints

### GET /api/records

按时间粒度查询记录列表。

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| view | string | No | "day" | 时间粒度: day, week, month, year |
| date | string | No | today | 基准日期 (YYYY-MM-DD) |
| milestone_only | boolean | No | false | 仅显示里程碑记录 |
| page | integer | No | 1 | 分页页码 |
| page_size | integer | No | 20 | 每页数量 |

**Response 200**:
```json
{
  "items": [
    {
      "date": "2026-03-21",
      "media_count": 3,
      "text_count": 1,
      "first_thumbnail": "/api/media/1/thumbnail",
      "has_milestone": true,
      "milestone_name": "第一次翻身",
      "milestone_icon": "Trophy",
      "preview_text": "宝宝今天第一次..."
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

### GET /api/records/{date}

获取单日完整记录。

**Path Parameters**: `date` (string, YYYY-MM-DD)

**Response 200**:
```json
{
  "id": 1,
  "date": "2026-03-21",
  "created_at": "2026-03-21T10:00:00",
  "updated_at": "2026-03-21T15:30:00",
  "media_entries": [
    {
      "id": 1,
      "media_type": "image",
      "thumbnail_url": "/api/media/1/thumbnail",
      "file_url": "/api/media/1/file",
      "description": "宝宝的微笑",
      "file_size": 2048000,
      "original_filename": "IMG_001.jpg",
      "sort_order": 0
    }
  ],
  "text_entries": [
    {
      "id": 1,
      "content": "今天宝宝学会了翻身...",
      "sort_order": 1
    }
  ],
  "milestone": {
    "id": 1,
    "category_id": 1,
    "category_name": "身体发育",
    "name": "第一次翻身",
    "description": "宝宝在3个月大时第一次独立翻身"
  }
}
```

**Response 404**: `{"detail": "Record not found for date 2026-03-21"}`

### POST /api/records

创建新日期记录。

**Request Body**:
```json
{
  "date": "2026-03-21",
  "texts": [
    {"content": "宝宝今天很开心", "sort_order": 0}
  ]
}
```

**Response 201**: 同 GET /api/records/{date} 响应格式

**Response 409**: `{"detail": "Record already exists for date 2026-03-21"}`

### PUT /api/records/{date}

更新日期记录。

**Request Body**:
```json
{
  "texts": [
    {"id": 1, "content": "更新后的文字", "sort_order": 0},
    {"content": "新增的文字条目", "sort_order": 1}
  ]
}
```

**Response 200**: 同 GET /api/records/{date} 响应格式

### DELETE /api/records/{date}

删除单日记录及所有关联媒体文件。

**Response 204**: No Content

**Response 404**: `{"detail": "Record not found"}`
