# Research: 宝宝成长记录桌面应用

**Branch**: `001-baby-growth-timeline` | **Date**: 2026-03-21

## 1. Electron + Python 打包方案

### Decision: PyInstaller 单文件打包 + electron-builder extraResources

将 Python FastAPI 后端通过 PyInstaller 打包为平台原生可执行文件（macOS: Unix executable, Windows: .exe），electron-builder 将该文件作为 `extraResources` 捆绑进最终安装包。

### Rationale

- PyInstaller 将 Python 解释器和所有依赖打包为单一二进制文件，用户无需安装 Python 环境
- electron-builder 的 `extraResources` 机制天然支持按平台分发额外文件
- Electron main process 在 `app.on('ready')` 时 spawn 该可执行文件，`app.on('before-quit')` 时 kill

### Alternatives Considered

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| PyInstaller (chosen) | 无需用户安装 Python; 单文件分发 | 打包体积较大 (~80-120MB); macOS 需签名 | 最佳平衡 |
| python-shell (npm) | 实现简单 | 要求用户系统已安装 Python 3.11+; 版本不可控 | 不可接受 |
| 嵌入式 Python (libpython) | 进程内通信更快 | 极高复杂度; 跨平台兼容性差 | 过度工程化 |
| Node.js 原生实现 (无 Python) | 单一运行时; 更小体积 | 放弃 Python 生态 (Pillow/SQLAlchemy); 违反宪法 | 不符合技术选型 |

### Implementation Notes

```typescript
// electron/main.ts — Python 进程管理核心逻辑
import { app, BrowserWindow } from 'electron';
import { spawn, ChildProcess } from 'child_process';
import path from 'path';

let pythonProcess: ChildProcess | null = null;

function getBackendPath(): string {
  const isProd = app.isPackaged;
  if (isProd) {
    return path.join(process.resourcesPath, 'backend', 'babygrow-server');
  }
  // 开发模式直接运行 Python
  return 'python';
}

function startBackend(): Promise<void> {
  return new Promise((resolve, reject) => {
    const backendPath = getBackendPath();
    const args = app.isPackaged ? [] : ['-m', 'uvicorn', 'app.main:app', '--port', '18900'];
    pythonProcess = spawn(backendPath, args, { cwd: app.isPackaged ? undefined : 'backend' });

    pythonProcess.stdout?.on('data', (data) => {
      if (data.toString().includes('Application startup complete')) resolve();
    });
    pythonProcess.stderr?.on('data', (data) => console.error(`[backend] ${data}`));
    setTimeout(() => resolve(), 5000); // 超时兜底
  });
}
```

### electron-builder 配置

```yaml
# electron-builder.yml
extraResources:
  - from: "backend/dist/"
    to: "backend"
    filter: ["**/*"]
```

## 2. SQLite 访问方式

### Decision: SQLAlchemy 2.0 async + aiosqlite

### Rationale

- SQLAlchemy 2.0 提供现代化的 async/await API，与 FastAPI 的异步模型完美契合
- aiosqlite 是 SQLite 的异步包装器，避免阻塞事件循环
- ORM 模型提供类型安全和关系映射，减少手写 SQL 的错误风险
- SQLAlchemy 的 migration 工具 (Alembic) 支持数据库版本管理

### Alternatives Considered

| 方案 | 结论 |
|------|------|
| SQLAlchemy 2.0 async (chosen) | 成熟 ORM + 异步支持，最佳选择 |
| 原生 aiosqlite | 轻量但缺少 ORM，维护成本高 |
| Tortoise ORM | 社区较小，文档不如 SQLAlchemy 完善 |
| Peewee | 不支持原生异步 |

### 存储优化策略

- 数据库仅存储元数据（路径引用、描述文字、时间戳），不存储二进制媒体数据
- 媒体文件按日期分目录存储：`{data_dir}/media/YYYY/MM/DD/{uuid}.{ext}`
- 缩略图独立存储：`{data_dir}/thumbnails/YYYY/MM/DD/{uuid}_thumb.jpg`
- 使用 WAL (Write-Ahead Logging) 模式提升并发读写性能
- 数据库文件预估：500 条记录 × 2000 条条目 × ~100 字节/条 ≈ ~2MB（远低于 50MB 限制）

## 3. 图片处理

### Decision: Pillow + pillow-heif

### Rationale

- Pillow 是 Python 图片处理的事实标准，支持 JPEG/PNG 的缩略图生成
- pillow-heif 插件为 Pillow 添加 HEIC/HEIF 格式读取能力（iPhone 默认格式）
- 缩略图策略：保持宽高比，最大边不超过 400px，JPEG 质量 85%，平均约 20-50KB

### Implementation Notes

```python
# backend/app/services/media_processor.py
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

THUMBNAIL_MAX_SIZE = (400, 400)
THUMBNAIL_QUALITY = 85

async def generate_thumbnail(source_path: str, thumb_path: str) -> None:
    with Image.open(source_path) as img:
        img.thumbnail(THUMBNAIL_MAX_SIZE, Image.Resampling.LANCZOS)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(thumb_path, 'JPEG', quality=THUMBNAIL_QUALITY, optimize=True)
```

## 4. 视频缩略图

### Decision: ffmpeg-python 提取关键帧

### Rationale

- ffmpeg 是视频处理的工业标准，ffmpeg-python 提供 Python 接口
- 提取第 1 秒帧作为封面图，输出为 JPEG
- 需要系统安装 ffmpeg（macOS: `brew install ffmpeg`, Windows: 随应用捆绑）

### Implementation Notes

```python
import ffmpeg

async def generate_video_thumbnail(video_path: str, thumb_path: str) -> None:
    (
        ffmpeg
        .input(video_path, ss=1)
        .filter('scale', 400, -1)
        .output(thumb_path, vframes=1, format='image2', vcodec='mjpeg')
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )
```

## 5. EXIF 读取

### Decision: Pillow ExifTags

### Rationale

- Pillow 内置 EXIF 读取能力，无需额外依赖
- 主要读取 `DateTimeOriginal` (36867) 字段获取拍摄时间
- 作为记录日期的推荐默认值，用户可手动修改

### Implementation Notes

```python
from PIL import Image
from PIL.ExifTags import Tags

def extract_exif_date(image_path: str) -> str | None:
    try:
        with Image.open(image_path) as img:
            exif_data = img.getexif()
            date_str = exif_data.get(Tags.DateTimeOriginal.value)  # tag 36867
            if date_str:
                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S").strftime("%Y-%m-%d")
    except Exception:
        pass
    return None
```

## 6. 端口策略

### Decision: 默认 18900，自动递增检测

### Rationale

- 使用较高端口号 (18900) 避免与常用服务冲突
- 启动时检测端口可用性，若占用则自动 +1 尝试（最多 10 次）
- 端口号通过 Electron preload 脚本注入到渲染进程，确保前后端一致

### Implementation Notes

```python
# backend/app/config.py
import socket

def find_available_port(start: int = 18900, max_attempts: int = 10) -> int:
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available port in range {start}-{start + max_attempts}")
```

## 7. 前端路由

### Decision: vue-router, hash 模式

### Rationale

- Electron 加载本地文件使用 `file://` 协议，history 模式不支持
- hash 模式 (`/#/timeline`) 在 Electron 中完全兼容
- 路由结构：

| 路由 | 视图 | 说明 |
|------|------|------|
| `/#/` | TimelineView | 默认主视图 |
| `/#/record/:date` | RecordDetailView | 单日记录详情 |
| `/#/record/:date/edit` | RecordEditView | 记录编辑 |
| `/#/milestones` | MilestoneView | 里程碑总览 |
| `/#/settings` | SettingsView | 应用设置 |

## 8. 主题方案

### Decision: CSS 变量 + Element Plus 主题覆盖 + data-theme 属性切换

### Rationale

- 使用 CSS 自定义属性定义主题色板，通过 `document.documentElement.dataset.theme` 切换
- Element Plus 支持通过 CSS 变量覆盖组件主题色 (`--el-color-primary` 等)
- 3 个预设主题 + 1 个深色模式，切换即时生效，无需重载页面

### Theme Definitions

| 主题 | 主色 | 背景色 | 深色变体 |
|------|------|--------|----------|
| 简约白 (default) | #409EFF | #FFFFFF | #1a1a2e |
| 暖阳橙 (warm) | #E6A23C | #FFF8F0 | #2d1f0e |
| 夜空蓝 (night) | #6366F1 | #F0F0FF | #0f0f23 |

```css
/* src/themes/variables.css */
:root, [data-theme="default"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f7fa;
  --text-primary: #303133;
  --accent-color: #409eff;
  --milestone-color: #e6a23c;
}

[data-theme="warm"] {
  --bg-primary: #fff8f0;
  --bg-secondary: #fff0de;
  --text-primary: #4a3728;
  --accent-color: #e6a23c;
  --milestone-color: #f56c6c;
}

[data-theme="night"] {
  --bg-primary: #f0f0ff;
  --bg-secondary: #e8e8f8;
  --text-primary: #2d2d5e;
  --accent-color: #6366f1;
  --milestone-color: #a855f7;
}

[data-theme="default"].dark,
[data-theme="warm"].dark,
[data-theme="night"].dark {
  --bg-primary: var(--dark-bg);
  --bg-secondary: var(--dark-bg-secondary);
  --text-primary: #e0e0e0;
}
```
