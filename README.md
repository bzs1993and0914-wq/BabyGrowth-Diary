# BabyGrow 宝宝成长记录

一款桌面端宝宝成长记录应用，支持时间轴、日记、照片/视频、里程碑、成长曲线等功能。

### 账号、媒体与默认图（002 迭代）

- **登录 / 注册**：使用本地账号（用户名 + 密码），JWT 保存在浏览器 `localStorage`。未登录时除 `/login`、`/register` 外会跳转到登录页。
- **修改密码**：在「设置 → 账号与安全」中修改；登录失败与密码错误提示为统一文案，避免泄露账号是否存在。
- **媒体张数**：普通账号每条每日记录最多 **1** 个照片/视频；**VIP** 最多 **9** 个。后端与上传组件均会校验。设置页提供「普通 / VIP」体验开关（调用 `/api/auth/dev/set-tier`），便于本地验收。
- **上传失败默认图**：若用户尝试上传但全部失败，保存记录时可标记使用默认配图；详情与日记视图在无成功媒体且该标记为真时展示 `public/default-growth-placeholder.svg`（宝宝成长曲线主题）。
- **历史数据迁移**：若升级前已有记录、尚无用户表，首次启动会创建默认账号 **`local` / `changeme`**，并把旧记录挂到该账号下；请登录后尽快在设置中修改密码。

## 技术架构

| 层级 | 技术栈 | 说明 |
|------|--------|------|
| 桌面壳 | Electron 33+ | 封装前端与后端，提供原生窗口 |
| 前端 | Vue 3.5 + Vite 6 + Element Plus + Pinia | SPA 界面 |
| 后端 | Python 3.11 + FastAPI + SQLAlchemy 2.0 | REST API、数据处理 |
| 数据库 | SQLite (aiosqlite) | 本地持久化 |

---

## 项目结构

```
03-21/
├── src/                    # Vue 前端源码
├── electron/               # Electron 主进程与预加载脚本
├── backend/                # FastAPI 后端
├── specs/                  # 需求规格与契约
├── vite.config.ts
├── electron-builder.yml
└── package.json
```

---

## 一、前端模块

### 1.1 路由与页面

| 路由 | 组件 | 功能 |
|------|------|------|
| `/` | TimelineView | 时间轴首页，按日期展示记录卡片 |
| `/record/new` | RecordEditView | 新建每日记录 |
| `/record/:date` | RecordDetailView | 查看某日记录详情 |
| `/record/:date/edit` | RecordEditView | 编辑某日记录 |
| `/milestones` | MilestoneView | 里程碑列表与分类管理 |
| `/growth` | GrowthCurveView | 成长曲线（身高/体重/头围） |
| `/settings` | SettingsView | 应用设置、存储统计、导出、账号与改密等 |
| `/login` | LoginView | 登录 |
| `/register` | RegisterView | 注册 |

### 1.2 核心组件

| 组件 | 所在目录 | 说明 |
|------|----------|------|
| **TimelineCard** | timeline/ | 时间轴上的单日卡片 |
| **TimelineFilter** | timeline/ | 按类型筛选时间轴 |
| **MediaUploader** | media/ | 拖拽上传照片/视频，支持 JPG/PNG/HEIC/MP4/MOV |
| **ImagePreview** | media/ | 图片预览与全屏缩放 |
| **VideoPlayer** | media/ | 视频播放器 |
| **DiaryView** | record/ | 日记视图，展示文字与媒体 |
| **GrowthMetricInput** | record/ | 成长数据录入（身高、体重、头围） |
| **MilestonePicker** | record/ | 选择并关联里程碑 |

### 1.3 状态管理 (Pinia)

- **records**：当前记录、加载/保存/删除记录
- **auth**：登录态、令牌、当前用户与账号等级
- **settings**：应用设置、主题
- **milestones**：里程碑列表与分类

### 1.4 实现方式

- **构建**：Vite 6 打包到 `dist/`
- **API 调用**：axios 封装在 `src/api/`，baseURL 由 Electron preload 提供 (`http://localhost:18900`)
- **Hash 路由**：`createWebHashHistory()` 兼容 Electron 本地文件加载

---

## 二、后端模块

### 2.1 API 路由

| 前缀 | 文件 | 功能 |
|------|------|------|
| `/api/health` | health.py | 健康检查 |
| `/api/auth` | auth.py | 注册、登录、`/me`、修改密码、开发用等级切换 |
| `/api/records` | records.py | 按日期增删改查记录（按当前用户隔离） |
| `/api/media` | media.py | 媒体上传、获取文件、缩略图、删除 |
| `/api/milestones` | milestones.py | 里程碑与分类 CRUD |
| `/api/growth-metrics` | growth_metrics.py | 成长指标 CRUD |
| `/api/export` | export.py | 导出为压缩包 |
| `/api/settings` | settings.py | 应用设置读写 |

### 2.2 数据模型

- **DailyRecord**：每日记录，关联文本、媒体、里程碑、成长指标
- **MediaEntry**：照片/视频条目，存储路径、缩略图、描述
- **TextEntry**：文字日记
- **Milestone** / **MilestoneCategory**：里程碑及分类
- **GrowthMetric**：身高、体重、头围等

### 2.3 实现方式

- **存储**：SQLite 数据库 + 媒体文件按 `YYYY/MM/DD` 分层存储
- **媒体处理**：Pillow 缩略图、pillow-heif 处理 HEIC、ffmpeg-python 视频缩略图
- **数据目录**：`~/Library/Application Support/BabyGrow/`（macOS）或 `%APPDATA%/BabyGrow/`（Windows）

---

## 三、桌面应用 (Electron)

### 3.1 主进程 (electron/main.ts)

- 开发模式：使用 `spawn` 启动 `uvicorn` 运行 FastAPI
- 生产模式：启动打包后的 `babygrow-server` 可执行文件
- 创建 BrowserWindow，加载前端（开发时 `http://localhost:5173`，生产时 `dist/index.html`）

### 3.2 预加载脚本 (electron/preload.ts)

- 暴露 `window.electronAPI`：`apiBaseUrl`、`platform`
- 前后端通过 `http://localhost:18900` 通信

### 3.3 实现方式

- 使用 `vite-plugin-electron` 构建主进程和 preload
- 使用 `vite-plugin-electron-renderer` 为渲染进程启用 Node 预加载

---

## 项目启动

### 环境要求

| 工具 | 版本 |
|------|------|
| Node.js | >= 18.x |
| Python | >= 3.11 |
| ffmpeg | >= 5.x（视频缩略图） |

### 一键启动（推荐）

```bash
cd 03-21
npm install
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cd ..
# 初始化数据库（首次）
cd backend && python -m app.database.connection --init && cd ..

npm run dev
```

将同时启动：FastAPI 后端 (18900) + Vite 开发服务器 (5173) + Electron 窗口。

### 分步启动

**终端 1 - 后端：**
```bash
cd 03-21/backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 18900
```

**终端 2 - 前端 + Electron：**
```bash
cd 03-21
npm run dev:electron
```

---

## 项目打包

### 1. 构建前端

```bash
cd 03-21
npm run build
```

会执行 `vue-tsc --noEmit`、`vite build` 和 `electron-builder`，生成：

- `dist/`：前端静态资源
- `dist-electron/`：Electron 主进程与 preload
- `release/`：最终可安装包

### 2. 打包 Python 后端

需先单独打包后端可执行文件，供 Electron 生产模式使用：

```bash
cd 03-21/backend
pip install pyinstaller
pyinstaller --onefile --name babygrow-server app/main.py
```

生成 `backend/dist/babygrow-server`，electron-builder 的 `extraResources` 会将其打包进应用。

### 3. 打包桌面应用到电脑桌面

**完整构建流程：**

```bash
cd 03-21

# 1. 打包后端（生成 babygrow-server）
cd backend
source .venv/bin/activate
pip install pyinstaller
pyinstaller --onefile --name babygrow-server app/main.py
cd ..

# 2. 构建并打包 Electron 应用
npm run build
```

**输出位置：** `03-21/release/`

| 平台 | 安装包 |
|------|--------|
| macOS | `BabyGrow-0.1.0.dmg` 或 `BabyGrow-0.1.0-arm64.dmg` |
| Windows | `BabyGrow 0.1.0 Setup.exe` |

**安装到桌面：**

1. **macOS**：双击 `.dmg`，将 BabyGrow 拖入「应用程序」
2. **Windows**：运行 `Setup.exe`，按向导安装，可选择创建桌面快捷方式

安装后，应用数据存放在：

- macOS：`~/Library/Application Support/BabyGrow/`
- Windows：`%APPDATA%/BabyGrow/`

---

## 常用命令

| 命令 | 说明 |
|------|------|
| `npm run dev` | 开发模式（后端 + 前端 + Electron） |
| `npm run dev:electron` | 仅启动 Vite + Electron（需手动启动后端） |
| `npm run build` | 构建生产版本并打包 Electron |
| `npm run lint` | ESLint 检查 |
| `npm run format` | Prettier 格式化 |
| `cd backend && pytest` | 后端测试 |
| `cd backend && ruff check .` | 后端代码检查 |

---

## API 文档

后端启动后访问：

- Swagger UI：http://localhost:18900/docs
- ReDoc：http://localhost:18900/redoc
