# Settings API Contract

**Base Path**: `/api/settings`

## Endpoints

### GET /api/settings

获取所有应用设置。

**Response 200**:
```json
{
  "theme": "default",
  "dark_mode": false,
  "thumbnail_max_size": 400,
  "thumbnail_quality": 85
}
```

### PUT /api/settings

更新应用设置（部分更新）。

**Request Body**:
```json
{
  "theme": "warm",
  "dark_mode": true
}
```

**Response 200**: 同 GET /api/settings 响应格式（返回更新后的完整设置）

## Available Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| theme | string | "default" | 主题: default, warm, night |
| dark_mode | boolean | false | 深色模式开关 |
| thumbnail_max_size | integer | 400 | 缩略图最大边长 (px) |
| thumbnail_quality | integer | 85 | 缩略图 JPEG 质量 (1-100) |

### GET /api/health

健康检查端点，用于 Electron 主进程确认后端已启动。

**Response 200**:
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```
