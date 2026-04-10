# Tasks: Phase Three — Record Date Cap, Allergy, Reminder, Tray

**Input**: Design documents from `/specs/003-record-allergy-tray-reminders/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/records-phase-3.md](./contracts/records-phase-3.md), [research.md](./research.md), [quickstart.md](./quickstart.md)

**Tests**: 规格未强制 TDD；本列表**不包含**独立自动化测试任务，可按需在后端 `tests/` 补 pytest。

**Organization**: 按用户故事（US1–US4）分阶段；`electron/main.ts` 上 US3 与 US4 需同一人顺序改或单提交合并，避免冲突。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行（不同文件、无未完成的前置依赖）
- **[Story]**: US1 = 日期上限；US2 = 过敏；US3 = 10:00 提醒；US4 = 托盘
- 描述中须包含**确切文件路径**

## Path Conventions

仓库为 **Electron**（`electron/`）+ **Vue**（`src/`）+ **FastAPI**（`backend/app/`）。

---

## Phase 1: Setup（共享准备）

**Purpose**: 确认设计产物与仓库布局一致，便于实现阶段引用。

- [x] T001 Verify `specs/003-record-allergy-tray-reminders/plan.md`、contracts 与 `spec.md` 范围一致，并确认关键路径为 `backend/app/`、`src/`、`electron/`

---

## Phase 2: Foundational（阻塞所有用户故事）

**Purpose**: 数据库列、通用 Pydantic 字段、记录日期服务端校验基线——完成后各故事可在不同时序落地（US1 仅需日期校验亦可先演示）。

**⚠️ CRITICAL**: 未完成本阶段前，不应在发布分支合并仅前端日期限制而无后端校验的实现。

- [x] T002 [P] Add nullable `allergy_notes` (`Text`) on `DailyRecord` and SQLite `ALTER`/upgrade in `backend/app/models/daily_record.py` and `backend/app/database/schema_upgrade.py`（必要时联动 `backend/app/database/init_db.py`）
- [x] T003 [P] Extend `RecordCreate`、`RecordUpdate`、`RecordResponse`、`RecordListItem` with `allergy_notes` in `backend/app/schemas/records.py`
- [x] T004 Add helper `assert_record_date_not_after_today(date_str: str)`（或等价命名）在 `backend/app/api/records.py` 顶部或 `backend/app/services/` 新模块，供创建/更新复用

**Checkpoint**: 迁移可应用到现有 SQLite；schemas 与模型对齐；日期辅助函数可被路由调用。

---

## Phase 3: User Story 1 — 记录日期不得超过今天 (Priority: P1) 🎯 MVP

**Goal**: 前后端均阻止「今天」之后的记录日期。

**Independent Test**: 无需过敏字段即可验收：未来日不可选或 API 422/400；编辑记录改未来日失败（见 `quickstart.md` §1）。

### Implementation for User Story 1

- [x] T005 [US1] Call `assert_record_date_not_after_today` on `POST /records/` body `date` and on `PUT /records/{date}` when date changes in `backend/app/api/records.py`，返回清晰 `detail` 中文说明
- [x] T006 [P] [US1] Disable future days on record date picker（`disabled-date` 或等价）于 `src/views/RecordEditView.vue` 及任何其他选择记录日期的界面
- [x] T007 [US1] Surface date validation errors to user（toast/表单提示）于 `src/views/RecordEditView.vue` 或统一错误处理于 `src/api/client.ts`

**Checkpoint**: US1 可单独演示与验收（SC-001）。

---

## Phase 4: User Story 2 — 过敏食物警示与集中查看 (Priority: P2)

**Goal**: 编辑页 ⚠️ 过敏输入、列表高亮、首页入口、聚合列表 API。

**Independent Test**: 见 `quickstart.md` §2；不依赖托盘与提醒。

### Implementation for User Story 2

- [x] T008 [US2] Persist `allergy_notes` on create/update（含空白规范化）于 `backend/app/api/records.py` 内 `create_record`、`update_record`
- [x] T009 [US2] Implement `has_allergy=true` query（或 `GET /api/records/allergies` 备用）于 `backend/app/api/records.py`，行为对齐 `contracts/records-phase-3.md`
- [x] T010 [P] [US2] Add `allergy_notes`（及列表项需要字段）到 `src/types/api.ts`
- [x] T011 [US2] Add ⚠️ 警示样式的过敏文本域与展示于 `src/views/RecordEditView.vue`；若详情需展示则同步 `src/views/RecordDetailView.vue`
- [x] T012 [P] [US2] Add 醒目样式（颜色/文案）于 `src/components/timeline/TimelineCard.vue` 或 `src/components/timeline/TimelineGroup.vue`（当 `allergy_notes` 非空）
- [x] T013 [US2] Add `listRecords`/`fetchAllergies` 参数与响应映射于 `src/api/records.ts`（及必要时 `src/stores/records.ts`）
- [x] T014 [US2] Add entry on timeline home `src/views/TimelineView.vue`（或 `src/components/common/AppHeader.vue` 若产品更倾向全局入口）与新路由视图（如 `src/views/AllergyRecordsView.vue`）于 `src/router/index.ts`

**Checkpoint**: US2 独立可测；聚合页展示全部非空过敏记录。

---

## Phase 5: User Story 3 — 每日 10:00 提醒 (Priority: P3)

**Goal**: 每自然日本地 10:00 至多一次桌面通知，文案含义为「该给宝宝创建新的记录啦」。

**Independent Test**: 见 `quickstart.md` §3。

### Implementation for User Story 3

- [x] T015 [US3] Add `electron-store`（或 `research.md` 选定之等价）依赖，于 `package.json` 并在 `electron/main.ts` 初始化用于键 `lastDailyRecordNudgeDate`
- [x] T016 [US3] Implement local-time 10:00 check loop、`Notification`（或 `dialog` 降级）、按日去重于 `electron/main.ts`；在 macOS 按需请求通知权限

**Checkpoint**: US3 在主进程可单独验收（应用保持运行前提下）。

---

## Phase 6: User Story 4 — 关闭窗口 → 托盘恢复 (Priority: P4)

**Goal**: 关窗隐藏、托盘图标、点击恢复、菜单「退出」结束进程；Tray 失败时降级（见 `research.md` R-006）。

**Independent Test**: 见 `quickstart.md` §4。

### Implementation for User Story 4

- [x] T017 [US4] Implement `close` 拦截、`hide()`、`Tray` 图标（使用 `public/` 或打包内资源路径）、左键 `show`+`focus`、上下文菜单「退出」触发 `app.quit()` 与后端子进程清理；Tray 构造失败时回退为 `minimize` 于 `electron/main.ts`

**Checkpoint**: US4 可用且不出现不可恢复的悬空进程（SC-004）。

---

## Phase 7: Polish & Cross-Cutting

**Purpose**: 文档与手工回归。

- [x] T018 [P] Walk through `specs/003-record-allergy-tray-reminders/quickstart.md` and fix gaps（若发现路由/文案遗漏，补对应 `src/` 或 `electron/` 文件）
- [x] T019 [P] Ensure API types and list DTOs stay in sync after implementation passes review in `src/types/api.ts` and `backend/app/schemas/records.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 → 2 → 3+**：顺序执行；User Story 阶段默认按 P1→P4 以减少 `RecordEditView.vue` / `electron/main.ts` 冲突。
- **Polish**：依赖 US1–US4 中已纳入范围的故事完成。

### User Story Dependencies

- **US1**：仅依赖 Phase 2（尤其 T004）；与 US2 共享 `RecordEditView.vue` — 建议 US1 完成后再做 T011，或同一工作区连续提交。
- **US2**：依赖 Phase 2（T002、T003）；与 US1 共享同一记录表单文件。
- **US3 / US4**：依赖 Phase 2 较弱（数据无关），但**均修改 `electron/main.ts`** — 必须顺序化或单分支合并。

### Parallel Opportunities

- T002 ∥ T003 ∥ T004（不同关注点；T004 新文件时更方便并行）。
- T005 ∥ T006（后端 `records.py` vs 前端 `RecordEditView.vue`）。
- T010 ∥ T012（`api.ts` vs timeline 组件）。
- T018 ∥ T019（验证 vs 类型同步）。

### MVP 建议范围

- **最小可交付**：Phase 1 + Phase 2 + Phase 3（T001–T007）满足日期约束（SC-001）。

---

## Parallel Example: User Story 1

```bash
# 在 Phase 3 可同时进行：
# - T005: backend/app/api/records.py
# - T006: src/views/RecordEditView.vue
# 完成后执行 T007 统一错误展示。
```

---

## Implementation Strategy

1. 完成 Phase 1–2 → 数据库与校验基线就绪。  
2. 完成 Phase 3 → 停止并跑通 `quickstart.md` §1（MVP）。  
3. 增量交付 Phase 4（过敏）→ §2。  
4. Phase 5–6 在同一代码分支顺序修改 `electron/main.ts` → §3–§4。  
5. Phase 7 全量 quickstart。

---

## Notes

- 字段名以 `data-model.md` 的 `allergy_notes` 为建议名，若实现选用 `baby_allergy_foods` 须全栈一致并更新 contracts。  
- `records.py` 中 `_response_use_default_media_placeholder` 等行为与本期任务正交；修改时避免无关重构。  
- 任务勾选：将已完成项标为 `[x]`（本批次已全部勾选）。

## Summary

| 指标 | 值 |
|------|-----|
| 总任务数 | 19 |
| US1 | 3（T005–T007） |
| US2 | 7（T008–T014） |
| US3 | 2（T015–T016） |
| US4 | 1（T017） |
| Setup + Foundational + Polish | 6（T001–T004，T018–T019） |
