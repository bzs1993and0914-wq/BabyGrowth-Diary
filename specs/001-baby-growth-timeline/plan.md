# Implementation Plan: 宝宝成长记录桌面应用

**Branch**: `001-baby-growth-timeline` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-baby-growth-timeline/spec.md`

## Summary

构建一款基于 Electron 的桌面应用，帮助父母以时间轴形式记录宝宝的每日成长。应用采用双进程架构：Electron 主进程管理窗口和 Python 后端进程生命周期，Vue 3 渲染进程提供 UI，Python FastAPI 本地服务处理所有数据持久化和媒体处理。数据以「日」为最小单位组织，支持日/周/月/年四种粒度浏览，平铺/折叠两种视图，里程碑标记，日记式图文展示，以及多主题风格。

## Technical Context

**Language/Version**: TypeScript 5.x (Electron/Vue), Python 3.11+ (Backend)
**Primary Dependencies**: Electron 33+, Vue 3.5+, Element Plus 2.9+, Pinia 2.x, vue-router 4.x, axios; FastAPI 0.115+, SQLAlchemy 2.0, Pydantic v2, Pillow 11+, ffmpeg-python, pillow-heif, aiosqlite
**Storage**: SQLite (via SQLAlchemy 2.0 async + aiosqlite), 本地文件系统存储媒体文件
**Testing**: Vitest (前端单元测试), pytest + httpx (后端单元/集成测试)
**Target Platform**: macOS (优先), Windows
**Project Type**: desktop-app (Electron + Python sidecar)
**Performance Goals**: 应用启动 < 3s, 时间轴视图切换 < 1s, 滚动 60fps, 缩略图生成 < 2s
**Constraints**: 离线优先 (无网络依赖), 数据库 < 50MB (6个月使用), 单个视频 < 2GB, 3次点击完成核心操作
**Scale/Scope**: 单用户桌面应用, 预计 1000+ 条记录, 约 8 个页面/视图

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | 原则 | 验证项 | 状态 |
|---|------|--------|------|
| I | 用户体验优先 | 录入流程: FAB 按钮 → 编辑面板 → 保存 (3次点击); 支持深色模式 | PASS |
| II | 数据安全与隐私 | 全部本地存储, 无云服务, 无数据收集; 支持 ZIP 导出 | PASS |
| III | 离线优先 | FastAPI 本地运行, SQLite 本地数据库, 无网络依赖 | PASS |
| IV | 时间轴驱动 | 日期为主键, 支持日/周/月/年聚合查询, 里程碑分类筛选 | PASS |
| V | 媒体丰富性 | Pillow 处理图片 (JPEG/PNG/HEIC), ffmpeg-python 视频缩略图, EXIF 读取 | PASS |
| VI | 简洁至上 | MVP 优先实现 P1/P2, 模块化低耦合架构, 成熟技术栈 | PASS |

## Project Structure

### Documentation (this feature)

```text
specs/001-baby-growth-timeline/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
baby-grow/
├── electron/                     # Electron 主进程 (Node.js/TypeScript)
│   ├── main.ts                   # 窗口管理 + Python 进程生命周期
│   └── preload.ts                # contextBridge (提供 API base URL)
├── src/                          # Vue 3 渲染进程
│   ├── App.vue
│   ├── main.ts
│   ├── api/                      # Axios HTTP 客户端封装
│   │   ├── client.ts             # axios instance (baseURL: localhost:18900)
│   │   ├── records.ts
│   │   ├── media.ts
│   │   ├── milestones.ts
│   │   └── export.ts
│   ├── components/
│   │   ├── timeline/             # TimelineView, TimelineCard, TimelineFilter
│   │   ├── record/               # RecordEditor, RecordDetail, DiaryView
│   │   ├── media/                # ImagePreview, VideoPlayer, MediaUploader
│   │   └── common/               # AppHeader, ThemeSwitcher, EmptyState
│   ├── views/
│   │   ├── TimelineView.vue      # 主视图：时间轴浏览
│   │   ├── RecordDetailView.vue  # 记录详情/日记展示
│   │   ├── RecordEditView.vue    # 记录编辑
│   │   ├── MilestoneView.vue     # 里程碑总览
│   │   └── SettingsView.vue      # 设置（主题/存储/导出）
│   ├── stores/                   # Pinia 状态管理
│   │   ├── records.ts
│   │   ├── milestones.ts
│   │   └── settings.ts
│   ├── composables/              # Vue 组合式函数
│   ├── types/                    # TypeScript 类型定义
│   └── themes/                   # 主题 CSS 变量 (简约白/暖阳橙/夜空蓝)
├── backend/                      # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py               # FastAPI 入口 + CORS + lifespan
│   │   ├── config.py             # 配置 (数据目录/端口/缩略图尺寸)
│   │   ├── database/
│   │   │   ├── connection.py     # SQLAlchemy async engine + session
│   │   │   └── migrations/       # Alembic 迁移脚本
│   │   ├── models/               # SQLAlchemy ORM 模型
│   │   │   ├── daily_record.py
│   │   │   ├── media_entry.py
│   │   │   ├── text_entry.py
│   │   │   ├── milestone.py
│   │   │   └── milestone_category.py
│   │   ├── schemas/              # Pydantic 请求/响应模型
│   │   ├── api/                  # FastAPI 路由
│   │   │   ├── records.py
│   │   │   ├── media.py
│   │   │   ├── milestones.py
│   │   │   ├── export.py
│   │   │   └── settings.py
│   │   └── services/             # 业务逻辑
│   │       ├── media_processor.py  # 缩略图生成/HEIC转换/EXIF读取
│   │       ├── storage_manager.py  # 文件存储管理
│   │       └── export_service.py   # ZIP 导出
│   ├── requirements.txt
│   └── pyproject.toml
├── package.json
├── vite.config.ts
├── electron-builder.yml          # 打包配置 (含 Python 后端捆绑)
└── tsconfig.json
```

**Structure Decision**: 采用 Electron + Python sidecar 双进程架构。前端代码位于 `src/`（Vue 3 渲染进程），Electron 主进程代码位于 `electron/`，Python 后端代码位于 `backend/`。三者通过 HTTP REST API 解耦，便于独立开发和测试。

## Complexity Tracking

> 无 Constitution Check 违规项，无需复杂性追踪。
