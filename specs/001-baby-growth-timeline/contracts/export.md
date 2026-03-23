# Export & Storage API Contract

**Base Path**: `/api/export`, `/api/storage`

## Export Endpoints

### POST /api/export

触发数据导出，异步生成包含所有记录和媒体的 ZIP 文件。

**Request Body** (optional):
```json
{
  "date_from": "2026-01-01",
  "date_to": "2026-03-21"
}
```

**Response 202**:
```json
{
  "export_id": "abc123",
  "status": "processing",
  "message": "Export started"
}
```

### GET /api/export/status

查询当前导出任务的进度。

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| export_id | string | Yes | 导出任务 ID |

**Response 200 (processing)**:
```json
{
  "export_id": "abc123",
  "status": "processing",
  "progress": 65,
  "message": "Packing media files..."
}
```

**Response 200 (completed)**:
```json
{
  "export_id": "abc123",
  "status": "completed",
  "progress": 100,
  "file_path": "/path/to/BabyGrow_Export_2026-03-21.zip",
  "file_size": 1073741824
}
```

**Response 200 (failed)**:
```json
{
  "export_id": "abc123",
  "status": "failed",
  "progress": 0,
  "message": "Insufficient disk space"
}
```

## Storage Endpoints

### GET /api/storage/stats

获取存储使用统计。

**Response 200**:
```json
{
  "database_size": 2048000,
  "media_total_size": 5368709120,
  "thumbnail_total_size": 104857600,
  "total_records": 500,
  "total_media": 2000,
  "total_images": 1800,
  "total_videos": 200
}
```

## ZIP Export Format

导出的 ZIP 文件结构：

```
BabyGrow_Export_2026-03-21.zip
├── metadata.json              # 结构化元数据（所有记录/里程碑/分类）
├── media/                     # 原始媒体文件（保持日期分目录）
│   └── YYYY/MM/DD/
│       └── {filename}
└── README.txt                 # 导出说明（格式版本/恢复指南）
```

metadata.json 格式：
```json
{
  "version": "1.0",
  "exported_at": "2026-03-21T15:00:00",
  "records": [...],
  "milestone_categories": [...],
  "app_settings": {...}
}
```
