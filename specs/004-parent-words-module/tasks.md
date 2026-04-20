# Tasks: 父母有话说 & 顶层导航整合

**Input**: Design documents from `/specs/004-parent-words-module/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/parent-words-api.md](./contracts/parent-words-api.md), [research.md](./research.md), [quickstart.md](./quickstart.md)

**Tests**: 规格未强制 TDD；本列表**不包含**独立自动化测试任务，可按需在后端 `tests/` 补 pytest。

**Organization**: 按实现阶段分组（Phase 1–5），每阶段内部按用户故事映射；后端与前端可在不同阶段内并行推进。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行（不同文件、无未完成的前置依赖）
- **[Story]**: US1 = 创建心语；US2 = 浏览回顾；US3 = 导航整合；US4 = 角色设置；US5 = 编辑删除
- 描述中须包含**确切文件路径**

## Path Conventions

仓库为 **Electron**（`electron/`）+ **Vue**（`src/`）+ **FastAPI**（`backend/app/`）。

---

## Phase 1: Setup & 验证

**Purpose**: 确认设计产物与仓库布局一致。

- [x] T001 Verify `specs/004-parent-words-module/plan.md`、contracts 与 `spec.md` 范围一致，确认关键路径为 `backend/app/`、`src/`

---

## Phase 2: 后端数据模型与 Schema 升级（阻塞所有用户故事）

**Purpose**: 创建 `parent_words` 表、扩展 `media_entries` 和 `users` 表、Pydantic schemas——完成后前后端可并行推进。

**⚠️ CRITICAL**: 未完成本阶段前，不应开始 API 路由或前端功能开发。

- [x] T002 [P] [US1] Create `ParentWord` SQLAlchemy model in `backend/app/models/parent_word.py`：字段按 `data-model.md` 定义（`id`, `user_id`, `title`, `content`, `author_role`, `created_at`, `updated_at`），包含 `user` relationship 和 `media_entries` relationship（`cascade="all, delete-orphan"`）
- [x] T003 [P] [US1] Update `backend/app/models/__init__.py` import `ParentWord` from `parent_word` module，确保 `Base.metadata.create_all` 能自动建表
- [x] T004 [P] [US1] Extend `MediaEntry` model in `backend/app/models/media_entry.py`：新增 `parent_word_id` mapped_column（`ForeignKey("parent_words.id", ondelete="CASCADE"), nullable=True`）+ `parent_word` relationship；将 `daily_record_id` 改为 `nullable=True`（新 media 可能只关联 parent_word）
- [x] T005 [P] [US4] Extend `User` model in `backend/app/models/user.py`：新增 `parent_role` mapped_column（`Text, nullable=True`）
- [x] T006 [US1] Update `backend/app/database/schema_upgrade.py`：新增 `media_entries.parent_word_id` 和 `users.parent_role` 的 ALTER TABLE 逻辑（参照 `data-model.md` 示例代码）
- [x] T007 [P] [US1] Create Pydantic schemas in `backend/app/schemas/parent_words.py`：`ParentWordCreate`、`ParentWordUpdate`、`ParentWordListItem`、`ParentWordResponse`、`ParentWordListResponse`——字段定义对齐 `contracts/parent-words-api.md`
- [x] T008 [P] [US4] Extend auth schemas：在现有 `AuthUser` 响应类型中新增 `parent_role: str | None` 字段，确保 `/api/auth/me` 能返回该字段。新建 `ProfileUpdate` schema（`parent_role: str | None`）

**Checkpoint**: `parent_words` 表可自动创建；`media_entries` 和 `users` 表新列可通过 schema_upgrade 补齐；所有 Pydantic 模型就绪。

---

## Phase 3: 后端 API 路由（US1, US2, US4, US5）

**Purpose**: 实现 ParentWord CRUD + 媒体上传扩展 + 用户角色更新端点。

**依赖**: Phase 2 全部完成。

- [x] T009 [US1/US2/US5] Create ParentWord CRUD router in `backend/app/api/parent_words.py`：
  - `GET /api/parent-words/`：分页列表，按 `created_at DESC` 排序，`user_id` 过滤，`content_preview` 取前 80 字符，`first_thumbnail` 子查询，可选 `author_role` 筛选参数
  - `POST /api/parent-words/`：创建，`author_role` 默认回退到 `current_user.parent_role`
  - `GET /api/parent-words/{id}`：详情，`selectinload(media_entries)`
  - `PUT /api/parent-words/{id}`：部分更新，刷新 `updated_at`
  - `DELETE /api/parent-words/{id}`：级联删除 + 调用 `storage_manager` 清理媒体磁盘文件
- [x] T010 [US4] Add `PUT /api/auth/profile` endpoint in `backend/app/api/auth.py`：接受 `ProfileUpdate` body，更新 `current_user.parent_role`，返回 `AuthUser` 格式
- [x] T011 [US1] Extend media upload in `backend/app/api/media.py`：
  - `daily_record_id` 参数改为 `Optional[int] = Form(None)`
  - 新增 `parent_word_id: Optional[int] = Form(None)` 参数
  - 互斥校验：两者有且仅有一个非 None
  - ParentWord 关联时验证所有权（`parent_word.user_id == current_user.id`）
  - ParentWord 媒体数量上限为 5（不区分 tier）
  - 媒体下载/缩略图鉴权扩展：`get_current_user_flexible` 中增加对 `parent_word.user_id` 的检查
- [x] T012 Register `parent_words.router` in `backend/app/main.py` with `prefix="/api"`

**Checkpoint**: 全部 API 端点可通过 curl/httpie 测试；创建 → 列表 → 详情 → 编辑 → 删除闭环完整。

---

## Phase 4: 前端导航嵌套分组整合（US3）

**Purpose**: 将平铺 3 Tab 导航重构为嵌套分组「宝宝成长」+「父母有话说」，PC 端和移动端双端适配。

**依赖**: 无后端依赖，可与 Phase 3 并行。

- [x] T013 [P] [US3] Restructure `navItems` data in `src/components/common/AppHeader.vue`：从平铺数组改为分组结构，包含 `{ label: '宝宝成长', children: [...] }` 和 `{ label: '父母有话说', path: '/parent-words', name: 'parent-words', icon: EditPen }`；新增 `EditPen` 或 `Notebook` 图标 import
- [x] T014 [US3] Implement PC desktop dropdown navigation in `src/components/common/AppHeader.vue`：
  - 「宝宝成长」hover/click 展开下拉面板（纯 CSS `:hover` 或 `el-popover`），面板内列出 3 个子项
  - 「父母有话说」为直接可点击项
  - `isActive` 逻辑扩展：子路由选中时父级「宝宝成长」保持高亮（检查 `route.name` 是否在 children 的 name 列表中）
  - 下拉面板样式与现有导航视觉风格一致
- [x] T015 [US3] Implement mobile drawer grouped layout in `src/components/common/AppHeader.vue`：
  - 「宝宝成长」作为灰色分区标题（非可点击项），下方平铺 3 个子项
  - 分隔线后「父母有话说」作为独立可点击条目
  - 样式增加 `.mobile-nav-group-title` 类

**Checkpoint**: PC 端导航下拉可用、高亮逻辑正确；移动端抽屉分组清晰。参照 `quickstart.md` §1 验收。

---

## Phase 5: 前端类型、API 客户端与 Store（US1, US2）

**Purpose**: 建立前端数据层基础设施。

**依赖**: Phase 3 后端 API 就绪（至少 T009 完成）。可与 Phase 4 并行。

- [x] T016 [P] [US1] Add TypeScript types in `src/types/api.ts`：
  - `ParentWordCreate`、`ParentWordUpdate`
  - `ParentWordListItem`、`ParentWordResponse`、`ParentWordListResponse`
  - `ProfileUpdate`（`{ parent_role: string | null }`）
  - 扩展 `AuthUser` 增加 `parent_role?: string | null`
- [x] T017 [P] [US1] Create API client in `src/api/parentWords.ts`：
  - `getParentWords(params)` → `GET /api/parent-words/`
  - `getParentWord(id)` → `GET /api/parent-words/{id}`
  - `createParentWord(data)` → `POST /api/parent-words/`
  - `updateParentWord(id, data)` → `PUT /api/parent-words/{id}`
  - `deleteParentWord(id)` → `DELETE /api/parent-words/{id}`
  - `updateProfile(data)` → `PUT /api/auth/profile`
- [x] T018 [US1/US2] Create Pinia store in `src/stores/parentWords.ts`：
  - State: `items`, `total`, `loading`, `currentWord`, `page`, `pageSize`
  - Actions: `loadList(append?)`, `loadDetail(id)`, `create(data)`, `update(id, data)`, `remove(id)`, `nextPage`
  - Computed: `hasMore`
  - 模式参照 `src/stores/records.ts`
- [x] T019 [P] [US1] Register routes in `src/router/index.ts`：
  - `/parent-words` → `ParentWordsView` (name: `parent-words`)
  - `/parent-words/new` → `ParentWordEditView` (name: `parent-word-new`)
  - `/parent-words/:id/edit` → `ParentWordEditView` (name: `parent-word-edit`)
  - `/parent-words/:id` → `ParentWordDetailView` (name: `parent-word-detail`)
  - 全部 `meta: { requiresAuth: true }`

**Checkpoint**: 类型安全、API 客户端可调用、store 可管理状态、路由注册完毕。

---

## Phase 6: 前端核心视图组件（US1, US2）

**Purpose**: 实现列表页、编辑页、详情页——核心用户体验。

**依赖**: Phase 5（T016–T019）全部完成。

- [x] T020 [P] [US2] Create `ParentWordCard` component in `src/components/parent-words/ParentWordCard.vue`：
  - Props: `ParentWordListItem`
  - 展示：标题、正文摘要（`content_preview`）、创建时间、作者标签（爸爸/妈妈/父母）、缩略图（如有）
  - 点击整卡片跳转 `/parent-words/{id}`
  - 响应式：PC 端网格、移动端单列
- [x] T021 [US2] Create list view in `src/views/ParentWordsView.vue`：
  - 页面标题 + "写下心里话" 按钮（跳转 `/parent-words/new`）
  - `ParentWordCard` 网格列表（PC 端 2 列，移动端 1 列）
  - 无限滚动加载更多（参照 `TimelineView.vue` 的 scroll 监听 + `store.loadList(true)` 模式）
  - 空状态：复用 `EmptyState` 组件（icon: `✉️`，title: "还没有心里话"，description: "写下你想对宝宝说的第一句话吧"，actionText: "写下第一句话"，actionRoute: "/parent-words/new"）
  - `LoadingSkeleton` 首次加载
- [x] T022 [US1] Create edit view in `src/views/ParentWordEditView.vue`：
  - 全屏编辑页面，独立路由
  - 判断 `isNew`（`route.name === 'parent-word-new'`）
  - 表单：标题 `el-input`（maxlength 100）、正文 `el-input type="textarea"`（autosize）、作者身份 `el-radio-group`（爸爸/妈妈/不标注）
  - 图片区域：复用 `MediaUploader` 组件 + 缩略图网格（最多 5 张）
  - 新建模式：先调 `store.create()` 获取 `id`，再用 `id` 上传图片
  - 编辑模式：`onMounted` 从 `store.loadDetail(id)` 加载并预填充
  - 保存：校验标题/正文非空 → `store.create()` 或 `store.update()` → `router.push('/parent-words/{id}')`
  - 取消：`router.back()` 或 `router.push('/parent-words')`
  - 顶部 action bar：返回 + 保存按钮
- [x] T023 [US2] Create detail view in `src/views/ParentWordDetailView.vue`：
  - 标题 + 作者标签 + 时间信息
  - 正文全文展示（`white-space: pre-wrap` 保留换行）
  - 图片画廊（复用 `ImagePreview` 或简单 grid + lightbox）
  - Action buttons：编辑（跳 `/parent-words/{id}/edit`）、删除（`ElMessageBox.confirm` → `store.remove(id)` → `router.push('/parent-words')`）
  - 显示"最后编辑"时间（`updated_at !== created_at` 时）
  - 返回按钮（回列表）

**Checkpoint**: 创建 → 列表 → 详情 → 返回列表 闭环可走通。参照 `quickstart.md` §2, §4 验收。

---

## Phase 7: 用户角色设置 + 编辑/删除 + 草稿保存（US4, US5）

**Purpose**: 完善角色自动填充、内容编辑删除、草稿防丢失。

**依赖**: Phase 6 核心视图基本完成。

- [x] T024 [P] [US4] Extend auth store in `src/stores/auth.ts`：在 `user` ref 类型中包含 `parent_role`；新增 `updateProfile(data)` action 调用 `PUT /api/auth/profile`，成功后更新 `user.value.parent_role`
- [x] T025 [US4] Add "我的角色" UI in `src/views/SettingsView.vue`：
  - 新增 `el-card` 区块（放在主题切换附近）
  - `el-radio-group`：爸爸 / 妈妈（值为 `dad` / `mom`）
  - `@change` 时调用 `auth.updateProfile({ parent_role })`
  - 初始值从 `auth.user.parent_role` 读取
- [x] T026 [US4/US1] Author role auto-fill in `src/views/ParentWordEditView.vue`：
  - 新建模式：从 `auth.user.parent_role` 自动填充 `authorRole` ref
  - 编辑模式：从加载的记录 `author_role` 预填充
  - 用户可通过 `el-radio-group` 临时切换（不影响 profile 设置）
  - 映射显示：`dad` → "爸爸"、`mom` → "妈妈"、`null` → "父母"
- [x] T027 [US5] Implement edit/delete flows in `src/views/ParentWordDetailView.vue` and `src/views/ParentWordEditView.vue`：
  - 详情页"编辑"按钮 → `router.push('/parent-words/{id}/edit')`
  - 详情页"删除" → `ElMessageBox.confirm` → `store.remove(id)` → `ElMessage.success` → `router.push('/parent-words')`
  - 编辑页 `watch(route)` 加载对应记录数据（参照 `RecordEditView.vue` 模式）
  - 保存后跳详情页并显示"已保存"提示
- [x] T028 [US1] Create draft auto-save composable in `src/composables/useParentWordDraft.ts`：
  - `saveDraft(key, data)`: 存 `localStorage` 键 `pw-draft-{key}`
  - `loadDraft(key)`: 读取并解析 JSON
  - `clearDraft(key)`: 删除
  - Auto-save: `watchEffect` + `useDebounceFn`（2s debounce）+ 30s interval
  - 返回 `{ hasDraft, restoreDraft, clearDraft }`
- [x] T029 [US1] Integrate draft composable into `src/views/ParentWordEditView.vue`：
  - `onMounted`: 检测是否有草稿 → 弹出 `ElMessageBox.confirm("检测到未保存的草稿，是否恢复？")`
  - 编辑过程中自动保存到 localStorage
  - `handleSave` 成功后 `clearDraft`
  - 取消编辑时不清除草稿（下次进入仍可恢复）

**Checkpoint**: 角色设置 → 自动填充 → 编辑/删除 → 草稿恢复全部可用。参照 `quickstart.md` §5, §6, §7 验收。

---

## Phase 8: 打磨与跨组件验收

**Purpose**: 响应式布局、边界情况、全量手动验收。

**依赖**: Phase 6 + Phase 7 主要任务完成。

- [x] T030 [P] Responsive layout validation：确认列表页、编辑页、详情页在 PC（>767px）和移动端（≤767px）下布局正常——卡片网格 PC 双列 / 移动单列、编辑表单不溢出、导航切换正确
- [x] T031 [P] Edge case handling across views：
  - 图片上传：过大/格式不支持的错误提示（复用现有 `MediaUploader` 的校验逻辑）
  - 保存失败：网络错误时 toast 提示 + 内容不丢失（草稿已保存）
  - 空标题/正文：前端校验阻止提交
  - 列表空状态：正确展示引导性 `EmptyState`
- [x] T032 Walk through `specs/004-parent-words-module/quickstart.md` §1–§9 全量验收，fix gaps if found
- [x] T033 [P] Ensure API types stay in sync between `src/types/api.ts` and `backend/app/schemas/parent_words.py`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Backend Models + Schemas) ──────────────────┐
    ↓                                                 │
Phase 3 (Backend API Routes)     Phase 4 (Nav ── 可并行) │
    ↓                                ↓               │
Phase 5 (Frontend Types/API/Store/Router) ←───────────┘
    ↓
Phase 6 (Frontend Core Views)
    ↓
Phase 7 (Settings + Edit/Delete + Draft)
    ↓
Phase 8 (Polish & Validation)
```

### User Story Dependencies

| 用户故事 | 阻塞任务 | 关键文件 |
|---------|---------|---------|
| US1 创建心语 | T002→T009→T016→T022 | `parent_word.py`, `parent_words.py` (API), `ParentWordEditView.vue` |
| US2 浏览回顾 | T009→T018→T021→T023 | `parentWords.ts` (store), `ParentWordsView.vue`, `ParentWordDetailView.vue` |
| US3 导航整合 | T013→T014→T015 | `AppHeader.vue` |
| US4 角色设置 | T005→T010→T024→T025→T026 | `user.py`, `auth.py`, `SettingsView.vue` |
| US5 编辑删除 | T009→T027 | `ParentWordDetailView.vue`, `ParentWordEditView.vue` |

### Parallel Opportunities

- **Phase 2 内部**: T002 ∥ T004 ∥ T005 ∥ T007 ∥ T008（不同文件）
- **Phase 3 vs Phase 4**: 后端 API 与前端导航完全无依赖，可并行
- **Phase 5 内部**: T016 ∥ T017 ∥ T019（不同文件）
- **Phase 6 内部**: T020 ∥ T022 ∥ T023（不同 `.vue` 文件，但 T021 依赖 T020）
- **Phase 7 内部**: T024 ∥ T028（不同文件）
- **Phase 8 内部**: T030 ∥ T031 ∥ T033

### MVP 建议范围

- **最小可交付（P1 闭环）**: Phase 1 + 2 + 3 + 4 + 5 + 6（T001–T023）
  - 覆盖 US1（创建）、US2（浏览）、US3（导航）
  - 可独立演示与验收核心功能
- **完整交付**: + Phase 7 + 8（T024–T033）
  - 补齐 US4（角色）、US5（编辑删除）、草稿保存、打磨

---

## Implementation Strategy

1. 完成 Phase 1–2 → 数据模型与 schemas 就绪
2. **并行**推进 Phase 3（后端 API）+ Phase 4（前端导航）
3. 完成 Phase 5 → 前端数据层就绪
4. 完成 Phase 6 → 停止并跑通 `quickstart.md` §1–§4（MVP）
5. 增量交付 Phase 7（角色 + 编辑删除 + 草稿）→ §5–§7
6. Phase 8 全量 quickstart §1–§9

---

## Notes

- 媒体上传 `parent_word_id` 与 `daily_record_id` 互斥——修改 `media.py` 时注意不破坏现有记录上传流程
- `MediaEntry.daily_record_id` 改为 nullable 后，现有代码中直接查询 `MediaEntry.daily_record_id == x` 不受影响（旧数据该列均非空）
- `AppHeader.vue` 改动较大（导航重构），建议在独立 commit 中完成并单独验证
- `ParentWordEditView.vue` 参照 `RecordEditView.vue` 模式但简化——无日期选择、无成长指标、无里程碑
- P3 标签功能（US6, FR-015）不在本次任务范围内

## Summary

| 指标 | 值 |
|------|-----|
| 总任务数 | 33 |
| Phase 2 (Models/Schemas) | 7 (T002–T008) |
| Phase 3 (Backend API) | 4 (T009–T012) |
| Phase 4 (Navigation) | 3 (T013–T015) |
| Phase 5 (Frontend Infra) | 4 (T016–T019) |
| Phase 6 (Core Views) | 4 (T020–T023) |
| Phase 7 (Settings/Edit/Draft) | 6 (T024–T029) |
| Phase 8 (Polish) | 4 (T030–T033) |
| Setup | 1 (T001) |
| 新增文件 | ~12 |
| 修改文件 | ~12 |
