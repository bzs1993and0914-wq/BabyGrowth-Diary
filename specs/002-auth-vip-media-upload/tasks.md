# Tasks: 账号体系、VIP 多图与上传失败默认图

**Input**: Design documents from `/specs/002-auth-vip-media-upload/`  
**Prerequisites**: [plan.md](./plan.md)（已创建）, [spec.md](./spec.md)（用户故事 P1–P3）

**Tests**: 规格未要求 TDD；本任务列表**不包含**独立测试任务，可在实现阶段按需补充。

**Organization**: 按用户故事拆分，便于分阶段交付与并行开发。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行（不同文件、无未完成的前置依赖）
- **[Story]**: 对应 spec 中的 User Story（US1 / US2 / US3）
- 描述中须包含**确切文件路径**

## Path Conventions

本仓库为 **Electron + Vue 前端**（`src/`、`electron/`）与 **FastAPI 后端**（`backend/app/`）；任务路径与之对齐。

---

## Phase 1: Setup（共享准备）

**Purpose**: 补齐本特性的规划文档，便于 `/speckit.plan` 与后续实现引用一致。

- [x] T001 Verify `specs/002-auth-vip-media-upload/plan.md` matches spec scope and repository layout under `src/`, `backend/app/`, `electron/`

---

## Phase 2: Foundational（阻塞所有用户故事的基础设施）

**Purpose**: 用户模型、本地认证、受保护 API、前端令牌注入——**完成后**才能安全地做多用户配额与路由守卫。

**⚠️ CRITICAL**: 未完成本阶段前，不应合并「仅前端假登录」与「未鉴权开放上传」到发布分支。

- [x] T002 [P] Add `User` SQLAlchemy model with password hash and `account_tier` (normal/vip) in `backend/app/models/user.py` and export in `backend/app/models/__init__.py`
- [x] T003 Add `user_id` foreign key on `DailyRecord` and `use_default_media_placeholder` boolean (or equivalent) on `backend/app/models/daily_record.py`
- [x] T004 Add SQLite schema upgrade path for existing databases (ALTER TABLE or migration script) in `backend/app/database/init_db.py` or new `backend/app/database/schema_upgrade.py`
- [x] T005 [P] Add Pydantic auth schemas (register, login, token response, change password) in `backend/app/schemas/auth.py`
- [x] T006 Implement password hashing, verification, and JWT creation/validation in `backend/app/services/auth_service.py`
- [x] T007 Add FastAPI auth routes (POST register, POST login, POST change-password) in `backend/app/api/auth.py` and include router in `backend/app/main.py`
- [x] T008 Add `get_current_user` / optional auth dependencies in `backend/app/api/deps.py`
- [x] T009 Apply authentication dependencies to record and media endpoints in `backend/app/api/records.py` and `backend/app/api/media.py`
- [x] T010 [P] Add `src/api/auth.ts` calling auth endpoints and extend shared types in `src/types/api.ts`
- [x] T011 Update `src/api/client.ts` request interceptor to attach `Authorization` bearer token from Pinia/local storage
- [x] T012 Add Pinia `src/stores/auth.ts` (login, logout, token persistence, current user/tier)

**Checkpoint**: 后端可注册/登录/改密，前端可携带令牌；记录与媒体接口在受保护模式下可用。

---

## Phase 3: User Story 1 — 可靠的照片记录与失败时的默认展示 (Priority: P1) 🎯 MVP

**Goal**: 当保存后没有任何成功入库的照片时，在查看页展示统一的「宝宝成长曲线」主题默认图；上传失败时与记录保存流程协同，避免裂图/空白。

**Independent Test**: 在「全部照片未能保存但记录已保存」场景下打开记录，应看到默认配图与文案；无成功图时不展示损坏占位。

### Implementation for User Story 1

- [x] T013 [P] [US1] Add default growth-curve placeholder image asset under `public/` (or `src/assets/`) and import/use in `src/components/record/DiaryView.vue`
- [x] T014 [US1] Extend record create/update schemas and handlers in `backend/app/schemas/records.py` and `backend/app/api/records.py` to persist `use_default_media_placeholder` on `DailyRecord`
- [x] T015 [US1] Update `src/views/RecordEditView.vue` and `src/components/media/MediaUploader.vue` to set placeholder flag when user attempted uploads but zero `MediaEntry` rows succeeded before save
- [x] T016 [US1] Update `src/components/record/DiaryView.vue` to show default placeholder when `media_entries.length === 0` and placeholder flag matches spec (and keep text-only behavior when no placeholder)
- [x] T017 [US1] Pass new props from `src/views/RecordDetailView.vue` into `DiaryView.vue` if record payload includes placeholder fields

**Checkpoint**: US1 可独立演示：无成功媒体时默认图可见；有成功媒体时仅展示成功媒体。

---

## Phase 4: User Story 2 — 注册、登录与修改密码 (Priority: P2)

**Goal**: 提供注册、登录、登录后修改密码的完整界面与导航；错误提示符合 FR-009（不泄露账户枚举信息）。

**Independent Test**: 不依赖 VIP 逻辑即可完成注册→登录→改密→用新密码登录。

### Implementation for User Story 2

- [x] T018 [P] [US2] Add `src/views/LoginView.vue` and `src/views/RegisterView.vue` wired to `src/api/auth.ts` and `src/stores/auth.ts`
- [x] T019 [US2] Add change-password form (section or dialog) in `src/views/SettingsView.vue` or new `src/views/AccountSecurityView.vue` using `src/api/auth.ts`
- [x] T020 [US2] Register routes in `src/router/index.ts` and add `beforeEach` guards; add header entry in `src/components/common/AppHeader.vue` for login/logout

**Checkpoint**: US2 可在 UI 层完整走完，与 US1/US3 可分别验收。

---

## Phase 5: User Story 3 — VIP 多图上传与按张数排列浏览 (Priority: P3)

**Goal**: 普通用户单次最多 1 张；VIP 单次最多 9 张；查看页按 1～9 张自适应布局（单张、并排、网格等）。

**Independent Test**: 使用不同 `account_tier` 账号保存记录，查看页张数与版式符合上限。

### Implementation for User Story 3

- [x] T021 [US3] Enforce per-request media count limits by `account_tier` in `backend/app/api/media.py` (reject excess with clear error)
- [x] T022 [US3] Enforce the same limits in `src/components/media/MediaUploader.vue` and `src/views/RecordEditView.vue` (disable multi-select or show message before upload)
- [x] T023 [US3] Refactor `src/components/record/DiaryView.vue` layout to switch arrangement by `mediaEntries.length` (1–9); adjust `src/components/timeline/TimelineCard.vue` thumbnails if detail view alone is insufficient for spec SC-005
- [x] T024 [P] [US3] Expose or mock `account_tier` (e.g. toggle in `src/views/SettingsView.vue` for dev) to support manual acceptance of VIP vs normal

**Checkpoint**: 配额与版式在前后端一致，可验收 SC-003 / SC-005。

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 文档与跨故事一致性。

- [x] T025 [P] Update `README.md` with login, VIP limits, and default-image behavior for end users
- [x] T026 [P] Align user-facing error strings for auth in `backend/app/api/auth.py` and `src/views/LoginView.vue` with FR-009 (no account enumeration)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 无依赖，可立即完成（T001 可与文档同步）。
- **Phase 2 (Foundational)**: 依赖 Phase 1 完成概念对齐；**阻塞** US1/US2/US3 中涉及 API 与数据模型的实现。
- **Phase 3 (US1)**: 依赖 Phase 2 中 `DailyRecord` 扩展与记录 API（若默认图仅前端展示且不需持久化，可最小化 T014，但仍建议与后端字段一致）。
- **Phase 4 (US2)**: 依赖 Phase 2 的 auth API 与 `src/stores/auth.ts`。
- **Phase 5 (US3)**: 依赖 Phase 2 的 `account_tier` 与受保护 `media` 路由；逻辑上在 US2 可登录后更易测，但可与 US4 UI 并行由不同开发者分担。
- **Phase 6 (Polish)**: 依赖计划交付的用户故事完成度。

### User Story Dependencies

- **US1 (P1)**: 在 Phase 2 完成后即可开始；默认图资源与 `DiaryView` 可与后端字段任务并行（T013、T014）。
- **US2 (P2)**: 依赖 Phase 2；与 US1 无强依赖，可并行。
- **US3 (P3)**: 依赖 Phase 2；**依赖** 用户可登录（US2）以便在 UI 中切换/验证 VIP，**或** 使用 T024 的开发开关在 US2 未完成时做后端测试。

### Within Each User Story

- 后端配额（T021）与前端限制（T022）应同一迭代合并，避免前后不一致。
- `DiaryView` 默认图（US1）与多图排版（US3）均修改同一文件：建议先合并 US1，再在同一文件上扩展 US3 布局，减少冲突。

### Parallel Opportunities

- **Phase 2**: T002、T005、T010 可并行（模型、schemas、前端 API 封装）。
- **US1**: T013（静态资源）与 T014（后端 schema）可并行。
- **US2**: T018（登录/注册页）与 T019（改密 UI）可并行（不同文件）。
- **US3**: T024 可与 T021–T023 并行（不同关注点）。
- **Polish**: T025、T026 可并行。

---

## Parallel Example: User Story 1

```bash
# 可同时进行：
Task T013: 在 `public/` 或 `src/assets/` 添加默认图并在 `DiaryView.vue` 引用
Task T014: 在 `backend/app/schemas/records.py` 与 `backend/app/api/records.py` 持久化占位字段
```

---

## Parallel Example: User Story 3

```bash
# 可同时进行：
Task T021: 在 `backend/app/api/media.py` 按 tier 校验数量
Task T024: 在 `src/views/SettingsView.vue` 增加 tier 切换或说明
```

---

## Implementation Strategy

### MVP First（仅 User Story 1）

1. 完成 Phase 1（T001）与 Phase 2（T002–T012）——认证与数据基础就绪。  
2. 完成 Phase 3（T013–T017）——默认图与上传失败兜底。  
3. **停止并验收**：在「全部上传失败」场景下确认默认图与记录正文一致。  

### Incremental Delivery

1. Setup + Foundational → 令牌与受保护 API 可用。  
2. + US1 → 默认图与媒体失败体验 → 可演示 P1。  
3. + US2 → 完整账号流程 → 可演示 P2。  
4. + US3 → VIP 配额与多图排版 → 可演示 P3。  
5. Polish → 文档与错误文案统一。  

### Parallel Team Strategy

1. 全员完成 Phase 2。  
2. 开发者 A：US1（`DiaryView` / `MediaUploader` / `records` API）。  
3. 开发者 B：US2（`LoginView` / `RegisterView` / 路由守卫）。  
4. 开发者 C：US3（`media.py` 配额 + `DiaryView` 网格）。  
5. 合并前对齐 `DiaryView.vue` 与 `MediaUploader.vue` 的冲突。  

---

## Notes

- `[P]` 表示不同文件、无未完成依赖；合并同一文件时慎用并行。  
- 所有 `[USn]` 任务须映射到 spec 中对应验收场景。  
- 若需自动化测试，可在后续迭代向 `tests/` 与 `backend/tests/` 追加任务。  
- **格式校验**: 本文件任务行均为 `- [ ] Tnnn ...` 且含任务 ID 与文件路径；用户故事阶段任务均含 `[USn]` 标签。  

---

## Task Count Summary

| 区域 | 任务数 |
|------|--------|
| Phase 1 Setup | 1 |
| Phase 2 Foundational | 11 |
| Phase 3 US1 | 5 |
| Phase 4 US2 | 3 |
| Phase 5 US3 | 4 |
| Phase 6 Polish | 2 |
| **Total** | **26** |

| User Story | 任务数 |
|------------|--------|
| US1 | 5（T013–T017） |
| US2 | 3（T018–T020） |
| US3 | 4（T021–T024） |

**建议 MVP 范围**: Phase 1–3（T001–T017），对应 spec 中 **P1（US1）**。
