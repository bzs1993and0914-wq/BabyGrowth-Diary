# Implementation Plan: 父母有话说 & 顶层导航整合

**Branch**: `004-parent-words-module` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/004-parent-words-module/spec.md`

## Summary

在现有 **Electron + Vue 3 + FastAPI + SQLAlchemy/SQLite** 架构上交付：（1）新增独立的「父母有话说」模块，支持父母创建、浏览、编辑、删除带有标题/正文/图片附件的"心里话"记录；（2）将顶层导航从平铺 3 Tab 重构为嵌套分组——「宝宝成长」（可展开含时间轴/里程碑/成长曲线）+「父母有话说」（独立顶级入口），PC 端与移动端双端适配；（3）在用户模型中新增 `parent_role`（爸爸/妈妈）属性并集成到设置页面，创建心语时自动填充并允许单条覆盖；（4）全屏独立编辑页面 + 本地草稿自动保存。

技术路径概要：SQLite 新增 `parent_words` 表 + `media_entries` 表扩展 `parent_word_id` 外键 + `users` 表扩展 `parent_role` 列；FastAPI 新增 `/api/parent-words` CRUD 路由 + 媒体上传接口扩展；Vue 前端新增 4 个视图组件 + Pinia store + API 客户端 + 导航嵌套分组重构。

## Technical Context

**Language/Version**: Python 3.11+（后端）、TypeScript 5.x（前端/Electron 主进程）  
**Primary Dependencies**: FastAPI 0.115+、SQLAlchemy 2.0、Pydantic v2、Electron 33+、Vue 3.5+、Element Plus 2.9+、Pinia 2.x、Vite  
**Storage**: SQLite（结构化数据）；草稿自动保存使用 `localStorage`  
**Testing**: pytest（后端路由与校验）；前端人工验收清单（见 quickstart）  
**Target Platform**: macOS（优先）、Windows 桌面  
**Project Type**: 桌面应用（Electron）+ 本地嵌入式 FastAPI 服务  
**Performance Goals**: 列表首次加载 ≤2s（本地 SQLite 查询，含 20 条分页）；编辑页保存 ≤1s  
**Constraints**: 离线优先、数据不出本地；图片上传复用现有媒体管道；P3 标签功能不在本期实现  
**Scale/Scope**: 单用户/少量用户本地库；新增 1 表 + 扩展 2 表列 + 6 个 API 端点 + 4 个前端视图 + 导航重构

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原则 | 评估 |
|------|------|
| I 用户体验优先 | 通过：嵌套导航清晰分区、全屏沉浸编辑、草稿自动保存防丢失、空状态引导首次使用 |
| II 数据安全与隐私 | 通过：所有数据留在本机 SQLite + 本地文件系统；父母心语使用同一认证与权限体系 |
| III 离线优先 | 通过：全部读写走本地后端，草稿保存到 localStorage，无外网依赖 |
| IV 时间轴驱动 | 通过：父母心语按时间倒序展示，与宝宝成长时间轴互补 |
| V 媒体丰富性 | 通过：复用现有图片上传管道，支持每条心语最多 5 张图片 |
| VI 简洁至上 | 通过：复用已有的媒体/认证/设置体系，不引入新的外部依赖 |

**Post-Phase 1**: 契约与数据模型未引入违反宪法的复杂层；无需填写 Complexity Tracking。

## Project Structure

### Documentation (this feature)

```text
specs/004-parent-words-module/
├── plan.md              # 本文件
├── research.md          # Phase 0 技术调研
├── data-model.md        # Phase 1 数据模型
├── quickstart.md        # Phase 1 手动验收指南
├── contracts/           # Phase 1 API 契约
│   └── parent-words-api.md
├── checklists/
│   └── requirements.md  # 规格质量清单
├── spec.md              # 功能规格说明
└── tasks.md             # /speckit.tasks（本命令不生成）
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── parent_word.py          # 新增：ParentWord 模型
│   │   └── __init__.py             # 更新：导入 ParentWord
│   ├── schemas/
│   │   ├── parent_words.py         # 新增：Pydantic 请求/响应模型
│   │   └── settings.py             # 更新：新增 parent_role 字段
│   ├── api/
│   │   ├── parent_words.py         # 新增：CRUD 路由
│   │   └── media.py                # 更新：支持 parent_word_id
│   ├── database/
│   │   └── schema_upgrade.py       # 更新：ALTER TABLE 补列
│   ├── models/user.py              # 更新：新增 parent_role 列
│   └── main.py                     # 更新：注册新路由

src/
├── api/
│   └── parentWords.ts              # 新增：API 客户端
├── stores/
│   └── parentWords.ts              # 新增：Pinia store
├── types/
│   └── api.ts                      # 更新：新增类型定义
├── views/
│   ├── ParentWordsView.vue         # 新增：列表页
│   ├── ParentWordEditView.vue      # 新增：创建/编辑页
│   └── ParentWordDetailView.vue    # 新增：详情页
├── components/
│   └── parent-words/
│       └── ParentWordCard.vue      # 新增：列表卡片组件
├── composables/
│   └── useParentWordDraft.ts       # 新增：草稿自动保存 composable
├── components/common/
│   └── AppHeader.vue               # 更新：嵌套分组导航
├── stores/settings.ts              # 更新：增加 parentRole
├── views/SettingsView.vue          # 更新：角色选择 UI
└── router/index.ts                 # 更新：新增路由
```

**Structure Decision**: 沿用仓库既有「`backend/` + `src/` + `electron/`」桌面应用布局；本特性不新增独立微服务或移动端工程。新增的前端组件按功能域归入 `parent-words/` 子目录，与现有 `timeline/`、`record/` 等并列。

## Complexity Tracking

> 无宪法违规项需特批；本节留空。

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |

## Implementation Phases

### Phase 1: 后端数据模型 + API（US-1, US-2, US-5 后端部分）

1. 新建 `ParentWord` SQLAlchemy 模型与数据库表
2. 扩展 `MediaEntry` 模型支持 `parent_word_id` 外键
3. 扩展 `User` 模型支持 `parent_role` 列
4. 更新 `schema_upgrade.py` 处理既有数据库的列迁移
5. 新建 Pydantic schemas 与 CRUD API 路由
6. 扩展媒体上传接口支持 `parent_word_id`
7. 扩展设置 API 返回/更新 `parent_role`

### Phase 2: 前端导航整合（US-3）

1. 重构 `AppHeader.vue` 导航数据结构为嵌套分组
2. PC 端：实现「宝宝成长」下拉展开 + 「父母有话说」顶级入口
3. 移动端：底部抽屉中分组标题 + 子项布局
4. 路由高亮逻辑适配嵌套结构

### Phase 3: 前端核心页面（US-1, US-2）

1. 新建 `parentWords` Pinia store + API 客户端
2. 实现列表页 `ParentWordsView.vue`（卡片列表 + 分页 + 空状态）
3. 实现全屏编辑页 `ParentWordEditView.vue`（表单 + 图片上传 + 草稿自动保存）
4. 实现详情页 `ParentWordDetailView.vue`
5. 注册新路由

### Phase 4: 设置与角色 + 编辑/删除（US-4, US-5）

1. 扩展设置页面 UI（"我的角色"选项）
2. 编辑页自动填充 + 临时切换作者身份
3. 实现编辑与删除功能
4. 草稿自动保存 composable（`useParentWordDraft`）

### Phase 5: 打磨与验收

1. PC/移动端响应式布局验证
2. 边界情况处理（网络失败、图片限制、空内容等）
3. 手动验收清单执行
