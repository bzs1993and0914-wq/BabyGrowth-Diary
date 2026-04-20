# API Contract: Parent Words（父母心语）

基路径与现有应用一致：`/api`。所有路由需携带 `Authorization: Bearer {token}`。

## 数据类型

### ParentWordCreate（请求体）

```json
{
  "title": "string (必填, 1-100字符)",
  "content": "string (必填, ≥1字符)",
  "author_role": "string | null (可选: 'dad' / 'mom' / null)"
}
```

### ParentWordUpdate（请求体）

```json
{
  "title": "string | undefined (可选)",
  "content": "string | undefined (可选)",
  "author_role": "string | null | undefined (可选: 'dad' / 'mom' / null)"
}
```

### ParentWordListItem（列表响应项）

```json
{
  "id": 1,
  "title": "给宝宝的第一封信",
  "content_preview": "亲爱的宝宝，今天是你出生的第30天...",
  "author_role": "mom",
  "media_count": 2,
  "first_thumbnail": "/api/media/42/thumbnail",
  "created_at": "2026-04-14T10:30:00",
  "updated_at": "2026-04-14T10:30:00"
}
```

### ParentWordResponse（详情/创建/更新响应）

```json
{
  "id": 1,
  "title": "给宝宝的第一封信",
  "content": "亲爱的宝宝，今天是你出生的第30天，妈妈有很多话想对你说...",
  "author_role": "mom",
  "created_at": "2026-04-14T10:30:00",
  "updated_at": "2026-04-14T10:30:00",
  "media_entries": [
    {
      "id": 42,
      "media_type": "image",
      "original_path": "...",
      "thumbnail_path": "...",
      "description": null,
      "file_size": 1024000,
      "original_filename": "letter.jpg",
      "sort_order": 0,
      "created_at": "2026-04-14T10:31:00"
    }
  ]
}
```

### ParentWordListResponse（列表响应）

```json
{
  "items": [ParentWordListItem, ...],
  "total": 25,
  "page": 1,
  "page_size": 20,
  "total_pages": 2
}
```

## 端点

### 1. 列表查询

`GET /api/parent-words/`

**Query 参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | `int` | `1` | 页码 |
| `page_size` | `int` | `20` | 每页条数，最大 50 |
| `author_role` | `string` | — | 可选筛选：`dad` / `mom` |

**Response**: `200` → `ParentWordListResponse`

**行为**:
- 按 `created_at` 降序排列
- 仅返回当前登录用户的记录（`user_id` 过滤）
- `content_preview` 取正文前 80 个字符
- `first_thumbnail` 取该记录第一张图片的缩略图路径（无图返回 `null`）

### 2. 创建心语

`POST /api/parent-words/`

**Request Body**: `ParentWordCreate`

**Response**: `201` → `ParentWordResponse`

**行为**:
- `author_role` 若未提供或为 `null`，取当前用户的 `parent_role` 值（若用户也未设置则保留 `null`）
- `created_at` 和 `updated_at` 自动设为当前时间
- 返回完整记录（含空的 `media_entries` 列表）

**错误**:
- `422`: 标题/正文为空或超长

### 3. 获取详情

`GET /api/parent-words/{id}`

**Response**: `200` → `ParentWordResponse`

**错误**:
- `404`: 记录不存在或不属于当前用户

### 4. 更新心语

`PUT /api/parent-words/{id}`

**Request Body**: `ParentWordUpdate`

**Response**: `200` → `ParentWordResponse`

**行为**:
- 仅更新请求体中提供的字段（部分更新）
- `updated_at` 刷新为当前时间
- 返回更新后的完整记录

**错误**:
- `404`: 记录不存在或不属于当前用户
- `422`: 校验失败

### 5. 删除心语

`DELETE /api/parent-words/{id}`

**Response**: `204` No Content

**行为**:
- 级联删除关联的所有 `media_entries`（数据库层 `ON DELETE CASCADE`）
- 同时清理关联媒体的磁盘文件（原文件 + 缩略图）

**错误**:
- `404`: 记录不存在或不属于当前用户

## 媒体上传扩展

### `POST /api/media/upload`（已有端点，扩展参数）

**Form 参数变更**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `daily_record_id` | `int` (原必填 → 可选) | 关联的每日记录 ID |
| `parent_word_id` | `int` (新增, 可选) | 关联的心语记录 ID |

**互斥规则**: `daily_record_id` 和 `parent_word_id` 必须提供且仅提供一个。

**Response**: 不变，仍为 `MediaEntryResponse`

**错误新增**:
- `422`: 同时提供或均未提供两个关联 ID
- `404`: `parent_word_id` 对应的记录不存在或不属于当前用户
- `400`: 心语关联的图片数量已达上限（5 张）

**媒体数量限制**:
- `DailyRecord` 保持原有限制（`TIER_MEDIA_CAP_NORMAL` / `TIER_MEDIA_CAP_VIP`）
- `ParentWord` 固定限制 5 张图片，不区分 tier

## 用户角色 API

### `GET /api/auth/me`（已有端点，响应扩展）

**新增响应字段**:

```json
{
  "id": 1,
  "username": "zhfe",
  "account_tier": "vip",
  "parent_role": "dad"
}
```

### `PUT /api/auth/profile`（新增端点）

**Request Body**:

```json
{
  "parent_role": "dad"
}
```

**Response**: `200` → `AuthUser`（同 `/api/auth/me` 结构）

**行为**:
- 更新当前用户的 `parent_role` 字段
- `parent_role` 接受 `"dad"` / `"mom"` / `null`

## 错误格式

沿用现有 FastAPI `HTTPException` 格式：

```json
{
  "detail": "标题不能为空"
}
```

或 Pydantic `ValidationError` 自动格式：

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
