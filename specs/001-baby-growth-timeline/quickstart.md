# Quickstart Guide: BabyGrow 宝宝成长记录

**Branch**: `001-baby-growth-timeline` | **Date**: 2026-03-21

## 环境要求

| 工具 | 版本要求 | 用途 |
|------|---------|------|
| Node.js | >= 18.x | Electron 宿主 + 前端构建 |
| npm | >= 9.x | 包管理 |
| Python | >= 3.11 | FastAPI 后端 |
| pip | >= 23.x | Python 包管理 |
| ffmpeg | >= 5.x | 视频缩略图生成 |

### 系统级依赖安装

**macOS**:
```bash
brew install node python@3.11 ffmpeg
```

**Windows**:
```powershell
# 使用 winget 或手动下载安装
winget install OpenJS.NodeJS.LTS
winget install Python.Python.3.11
# ffmpeg: 从 https://ffmpeg.org/download.html 下载并添加到 PATH
```

## 安装步骤

### 1. 克隆项目

```bash
git clone <repo-url> baby-grow
cd baby-grow
```

### 2. 安装前端依赖

```bash
npm install
```

### 3. 安装后端依赖

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 4. 初始化数据库

```bash
cd backend
python -m app.database.connection --init
cd ..
```

## 开发模式

### 一键启动（推荐）

```bash
npm run dev
```

此命令将同时启动:
1. Python FastAPI 后端 (`uvicorn app.main:app --reload --port 18900`)
2. Vite 开发服务器 (热更新)
3. Electron 窗口

### 分步启动

如需分别调试前后端：

**终端 1 — 启动 Python 后端**:
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 18900
```

**终端 2 — 启动 Vite + Electron**:
```bash
npm run dev:electron
```

### API 调试

后端启动后可访问自动生成的 API 文档：
- Swagger UI: `http://localhost:18900/docs`
- ReDoc: `http://localhost:18900/redoc`

## 构建打包

### 1. 打包 Python 后端

```bash
cd backend
pip install pyinstaller
pyinstaller --onefile --name babygrow-server app/main.py
cd ..
```

生成的可执行文件位于 `backend/dist/babygrow-server`。

### 2. 构建 Electron 桌面应用

```bash
# 构建前端资产 + 打包 Electron 应用
npm run build
```

最终安装包位于 `dist/` 目录:
- macOS: `BabyGrow-{version}.dmg`
- Windows: `BabyGrow-{version}-setup.exe`

## 数据存储位置

应用数据存储在以下目录（用户数据，不在项目目录内）：

| 平台 | 路径 |
|------|------|
| macOS | `~/Library/Application Support/BabyGrow/` |
| Windows | `%APPDATA%/BabyGrow/` |

目录结构：
```text
BabyGrow/
├── babygrow.db              # SQLite 数据库
├── media/                   # 原始媒体文件
│   └── YYYY/MM/DD/          # 按日期分层
└── thumbnails/              # 缩略图缓存 (可重建)
    └── YYYY/MM/DD/
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `npm run dev` | 开发模式（前后端 + Electron 全启动） |
| `npm run dev:electron` | 仅启动 Vite + Electron（需手动启动后端） |
| `npm run build` | 构建生产版本 |
| `npm run lint` | 前端代码检查 (ESLint) |
| `npm run format` | 前端代码格式化 (Prettier) |
| `npm run test` | 运行前端测试 (Vitest) |
| `cd backend && pytest` | 运行后端测试 |
| `cd backend && ruff check .` | 后端代码检查 |
| `cd backend && black .` | 后端代码格式化 |

## 项目配置文件

| 文件 | 用途 |
|------|------|
| `package.json` | Node.js 依赖 + 脚本定义 |
| `vite.config.ts` | Vite 构建配置 |
| `electron-builder.yml` | Electron 打包配置 |
| `tsconfig.json` | TypeScript 编译配置 |
| `backend/pyproject.toml` | Python 项目配置 |
| `backend/requirements.txt` | Python 依赖 |
| `.eslintrc.cjs` | ESLint 代码规范 |
| `.prettierrc` | Prettier 格式化配置 |
