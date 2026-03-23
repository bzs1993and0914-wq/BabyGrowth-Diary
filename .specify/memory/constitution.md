<!--
  Sync Impact Report
  ===========================
  Version change: 1.0.0 → 1.1.0
  Modified principles: N/A
  Added sections:
    - Technology Stack: 新增 Python 服务端技术栈（FastAPI）
  Removed sections: N/A
  Modified sections:
    - Technology Stack: React → Vue, Zustand → Pinia, UI 组件库调整为 Vue 生态
    - Development Workflow: 新增 Python 代码质量标准（Black, Ruff, mypy）
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ reviewed (no changes needed — generic)
    - .specify/templates/spec-template.md ✅ reviewed (no changes needed — generic)
    - .specify/templates/tasks-template.md ✅ reviewed (no changes needed — generic)
    - .specify/templates/checklist-template.md ✅ reviewed (no changes needed — generic)
  Follow-up TODOs: None
-->

# BabyGrow 宝宝成长记录 Constitution

## Core Principles

### I. 用户体验优先 (UX-First)

应用的主要用户是新手父母，他们往往睡眠不足、时间紧张。所有交互设计 MUST 遵循以下规则：

- 核心操作（拍照/录像/添加记录）MUST 在 3 次点击以内完成
- 界面 MUST 简洁直观，避免信息过载
- 时间轴视图 MUST 作为应用的主要导航方式，支持按日/周/月/年浏览
- 里程碑事件（生日、翻身、爬行、走路等）MUST 在时间轴上有醒目的视觉标记
- 支持深色模式，方便夜间哺乳时使用

**理由**：新手父母的可用时间和精力极为有限，应用不能成为负担，而应是轻松愉悦的记录工具。

### II. 数据安全与隐私 (Data Safety & Privacy)

宝宝的照片和视频是极其私密的家庭数据。系统 MUST 保障数据安全：

- 所有数据 MUST 默认存储在本地，不上传至任何云服务（除非用户主动选择备份）
- 应用 SHOULD 支持可选的本地数据加密（数据仅在本地运行，不上传外网，优先级较低）
- 导出功能 MUST 以通用格式输出（如 ZIP 包含原始媒体文件 + JSON 元数据），避免供应商锁定
- 应用 MUST NOT 收集任何用户行为分析数据

**理由**：婴幼儿数据需要最高级别的隐私保护，用户必须对自己的数据拥有完全的控制权。

### III. 离线优先 (Offline-First)

应用 MUST 在完全无网络的环境下正常运行：

- 所有核心功能（记录、浏览、搜索、编辑）MUST 离线可用
- 数据存储 MUST 使用本地数据库（SQLite）
- 媒体文件 MUST 存储在本地文件系统中，数据库只存储引用路径和元数据
- 如未来添加云同步功能，MUST 支持冲突解决机制

**理由**：父母可能在任何环境下使用应用，网络状况不应影响记录宝宝的珍贵瞬间。

### IV. 时间轴驱动 (Timeline-Driven Architecture)

时间轴是应用的核心组织方式，所有内容 MUST 围绕时间维度组织：

- 每条记录 MUST 包含精确的时间戳
- 时间轴 MUST 支持多种粒度的浏览（日视图/周视图/月视图/年视图）
- 里程碑事件 MUST 支持自定义分类（身体发育、语言发展、情感互动、饮食变化等）
- 时间轴 MUST 支持成长曲线的可视化展示（身高、体重等可量化指标的趋势图）
- 支持按关键词、标签、日期范围搜索和筛选记录

**理由**：时间是宝宝成长的最自然维度，以时间轴为核心可以直观呈现成长历程。

### V. 媒体丰富性 (Rich Media Support)

应用 MUST 支持多种媒体类型的无缝集成：

- MUST 支持图片上传（JPEG、PNG、HEIC）
- MUST 支持视频上传（MP4、MOV），并生成缩略图预览
- 每个媒体文件 MUST 支持添加文字描述/备注
- MUST 支持纯文字记录（日记/笔记形式）
- 图片 MUST 支持缩放和全屏预览
- 视频 MUST 支持应用内播放
- 媒体文件 SHOULD 自动读取 EXIF 信息以获取拍摄时间

**理由**：宝宝的成长需要通过多种形式来记录，文字、图片和视频各有其不可替代的价值。

### VI. 简洁至上 (Simplicity & YAGNI)

开发过程 MUST 遵循简洁原则：

- 功能开发 MUST 从最小可行产品（MVP）开始，逐步迭代
- MUST NOT 引入当前不需要的功能或依赖
- 数据模型 MUST 保持简洁但具备良好的可扩展性
- 代码架构 MUST 清晰，模块间低耦合
- 优先使用成熟稳定的技术方案，避免过度工程化

**理由**：项目应在合理时间内交付可用产品，避免因过度设计而拖延。

## Technology Stack & Constraints

### 技术选型

**桌面端（Electron）**：

- **框架**：Electron（基于 Chromium + Node.js 的跨平台桌面应用框架）
- **前端**：Vue 3 + TypeScript（Composition API）
- **UI 组件库**：Ant Design Vue 或 Element Plus（Vue 生态的现代化组件库）
- **状态管理**：Pinia（Vue 官方推荐的状态管理库）
- **构建工具**：Vite + electron-builder

**服务端（Python）**：

- **Web 框架**：FastAPI（高性能异步 API 框架）
- **ORM**：SQLAlchemy 2.0（数据库操作）
- **本地数据库**：SQLite（通过 aiosqlite 异步访问）
- **媒体处理**：Pillow（图片处理）、ffmpeg-python（视频缩略图生成）
- **数据校验**：Pydantic v2（请求/响应模型校验）
- **Python 版本**：Python 3.11+

### 平台约束

- **目标平台**：macOS（优先）、Windows
- **最低系统要求**：4GB RAM，500MB 可用磁盘空间（不含用户媒体文件）
- **性能目标**：应用启动时间 < 3 秒，时间轴滚动 60fps，图片加载 < 500ms
- **媒体限制**：单个视频文件 MUST 不超过 2GB（超出时拒绝并提示用户），图片自动生成缩略图以优化列表性能

### 数据存储

- SQLite 数据库存储结构化数据（记录、里程碑、标签等元数据）
- 媒体文件存储在应用数据目录下的独立文件夹中
- 数据库与媒体文件通过相对路径关联，确保数据可迁移性

## Development Workflow

### 开发流程

- 采用功能分支工作流（feature branch workflow）
- 每个用户故事作为独立的可交付单元开发和测试
- 代码提交 MUST 包含清晰的提交信息
- UI 变更 MUST 在 macOS 上验证视觉效果

### 质量标准

**前端（Vue + TypeScript）**：

- TypeScript 严格模式（strict: true）
- ESLint + Prettier 统一代码风格
- Vue 组件 MUST 使用 Composition API + `<script setup>` 语法

**服务端（Python）**：

- Black + Ruff 统一代码风格
- mypy 静态类型检查（strict 模式）
- FastAPI 路由 MUST 使用 Pydantic 模型定义请求/响应

**通用**：

- 关键业务逻辑 SHOULD 有单元测试覆盖
- 数据库操作 MUST 有错误处理和数据完整性校验
- 用户可见的错误信息 MUST 友好且有指导性

### 发布流程

- 使用 electron-builder 构建安装包
- 版本号遵循语义化版本（SemVer）
- 每个发布版本 MUST 包含更新日志

## Governance

本宪法是 BabyGrow 项目的最高指导文件，所有开发决策 MUST 与宪法原则保持一致。

- 所有代码审查 MUST 验证是否符合宪法原则
- 对宪法的修订 MUST 记录变更原因、影响范围和迁移计划
- 引入新的复杂性 MUST 提供充分的理由说明，并证明没有更简单的替代方案
- 宪法版本遵循语义化版本规则：MAJOR（原则删除/重定义）、MINOR（新增原则/章节）、PATCH（措辞调整/澄清）

**Version**: 1.1.0 | **Ratified**: 2026-03-21 | **Last Amended**: 2026-03-21
