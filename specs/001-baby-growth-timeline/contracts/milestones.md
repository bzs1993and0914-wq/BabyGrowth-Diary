# Milestones API Contract

**Base Path**: `/api/milestones`

## Endpoints

### POST /api/milestones

为日期记录标记里程碑。

**Request Body**:
```json
{
  "daily_record_id": 1,
  "category_id": 1,
  "name": "第一次翻身",
  "description": "宝宝在3个月大时第一次独立翻身"
}
```

**Response 201**:
```json
{
  "id": 1,
  "daily_record_id": 1,
  "category_id": 1,
  "category_name": "身体发育",
  "name": "第一次翻身",
  "description": "宝宝在3个月大时第一次独立翻身",
  "created_at": "2026-03-21T10:00:00"
}
```

**Response 409**: `{"detail": "Milestone already exists for this date"}`

### DELETE /api/milestones/{id}

取消里程碑标记。

**Response 204**: No Content

### GET /api/milestone-categories

获取所有里程碑分类（包含预设和自定义）。

**Response 200**:
```json
[
  {"id": 1, "name": "身体发育", "icon": "Trophy", "is_preset": true},
  {"id": 2, "name": "语言发展", "icon": "ChatDotRound", "is_preset": true},
  {"id": 3, "name": "情感互动", "icon": "Heart", "is_preset": true},
  {"id": 4, "name": "饮食变化", "icon": "Bowl", "is_preset": true},
  {"id": 5, "name": "其他", "icon": "Star", "is_preset": true},
  {"id": 6, "name": "社交发展", "icon": "User", "is_preset": false}
]
```

### POST /api/milestone-categories

创建自定义里程碑分类。

**Request Body**:
```json
{
  "name": "社交发展",
  "icon": "User"
}
```

**Response 201**:
```json
{"id": 6, "name": "社交发展", "icon": "User", "is_preset": false}
```

**Response 409**: `{"detail": "Category '社交发展' already exists"}`
