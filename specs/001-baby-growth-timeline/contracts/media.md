# Media API Contract

**Base Path**: `/api/media`

## Endpoints

### POST /api/media/upload

上传媒体文件（图片或视频）。

**Content-Type**: `multipart/form-data`

**Form Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | 媒体文件 (JPEG/PNG/HEIC/MP4/MOV) |
| daily_record_id | integer | Yes | 所属日期记录 ID |
| description | string | No | 配文/描述 |
| sort_order | integer | No (default: 0) | 排序序号 |

**Response 201**:
```json
{
  "id": 1,
  "media_type": "image",
  "thumbnail_url": "/api/media/1/thumbnail",
  "file_url": "/api/media/1/file",
  "description": "宝宝的微笑",
  "file_size": 2048000,
  "original_filename": "IMG_001.jpg",
  "exif_date": "2026-03-21",
  "sort_order": 0,
  "created_at": "2026-03-21T10:00:00"
}
```

**Response 400**: `{"detail": "Unsupported file type: .bmp"}`

**Response 413**: `{"detail": "Video file exceeds 2GB limit"}`

### GET /api/media/{id}/file

获取原始媒体文件（流式传输）。

**Response 200**: Binary file stream with appropriate Content-Type header

**Response 404**: `{"detail": "Media not found"}`

**Response 410**: `{"detail": "Media file is missing from disk"}`

### GET /api/media/{id}/thumbnail

获取缩略图。

**Response 200**: JPEG image binary

**Response 404**: `{"detail": "Thumbnail not found"}`

### PUT /api/media/{id}

更新媒体条目的描述或排序。

**Request Body**:
```json
{
  "description": "更新后的描述",
  "sort_order": 2
}
```

**Response 200**: 同 POST upload 响应格式

### DELETE /api/media/{id}

删除媒体条目及文件系统中的原始文件和缩略图。

**Response 204**: No Content
