# Tasks: 宝宝成长记录桌面应用

**Input**: Design documents from `/specs/001-baby-growth-timeline/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project scaffolding for Electron + Vue 3 + Python FastAPI

- [ ] T001 Initialize Node.js project with package.json (electron, vue, vite, element-plus, pinia, vue-router, axios, typescript dependencies) in `package.json`
- [ ] T002 Configure TypeScript with strict mode in `tsconfig.json` and `tsconfig.node.json`
- [ ] T003 [P] Configure Vite for Electron + Vue 3 in `vite.config.ts`
- [ ] T004 [P] Configure electron-builder with Python backend extraResources in `electron-builder.yml`
- [ ] T005 [P] Configure ESLint + Prettier for frontend in `.eslintrc.cjs` and `.prettierrc`
- [ ] T006 [P] Initialize Python project with pyproject.toml and requirements.txt (fastapi, uvicorn, sqlalchemy, aiosqlite, pydantic, pillow, pillow-heif, ffmpeg-python) in `backend/pyproject.toml` and `backend/requirements.txt`
- [ ] T006a [P] Configure Python code quality tools: Black, Ruff, mypy (strict mode) in `backend/pyproject.toml` and `backend/mypy.ini`
- [ ] T007 Create Electron main process entry with Python backend lifecycle management in `electron/main.ts`
- [ ] T008 Create Electron preload script exposing API base URL via contextBridge in `electron/preload.ts`
- [ ] T009 Create Vue 3 app entry with Element Plus, Pinia, vue-router setup in `src/main.ts`
- [ ] T010 Create root App.vue with router-view and theme provider in `src/App.vue`
- [ ] T011 [P] Create vue-router config with hash mode routes (timeline, record detail, record edit, milestones, settings) in `src/router/index.ts`
- [ ] T012 [P] Create axios HTTP client instance with baseURL localhost:18900 in `src/api/client.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T013 Create FastAPI app entry with CORS config and lifespan handler in `backend/app/main.py`
- [ ] T014 Create app config module with data directory, port, thumbnail settings in `backend/app/config.py`
- [ ] T015 Create SQLAlchemy async engine + session factory with WAL mode in `backend/app/database/connection.py`
- [ ] T016 Create DailyRecord SQLAlchemy model in `backend/app/models/daily_record.py`
- [ ] T017 [P] Create MediaEntry SQLAlchemy model in `backend/app/models/media_entry.py`
- [ ] T018 [P] Create TextEntry SQLAlchemy model in `backend/app/models/text_entry.py`
- [ ] T019 [P] Create Milestone SQLAlchemy model in `backend/app/models/milestone.py`
- [ ] T020 [P] Create MilestoneCategory SQLAlchemy model with preset seed data in `backend/app/models/milestone_category.py`
- [ ] T021 Create models __init__.py exporting all models and Base.metadata.create_all in `backend/app/models/__init__.py`
- [ ] T022 Create AppSettings key-value model in `backend/app/models/app_settings.py`
- [ ] T023 Create database initialization script (create tables + seed preset categories + default settings) in `backend/app/database/init_db.py`
- [ ] T024 Create health check endpoint GET /api/health in `backend/app/api/health.py`
- [ ] T025 [P] Create TypeScript type definitions for all API request/response models in `src/types/api.ts`
- [ ] T026 [P] Create TypeScript type definitions for frontend data models in `src/types/models.ts`
- [ ] T027 [P] Create CSS theme variables for 3 themes (default, warm, night) + dark mode in `src/themes/variables.css`
- [ ] T028 [P] Create storage manager service for file path resolution and directory creation in `backend/app/services/storage_manager.py`

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — 每日记录创建 (Priority: P1) MVP

**Goal**: 用户能够快速为宝宝创建每日记录，上传图片/视频并添加文字描述

**Independent Test**: 启动应用 → 点击"添加记录" → 选择日期 → 上传图片并输入描述 → 保存成功 → 在时间轴上看到记录

### Backend Implementation for US1

- [ ] T029 [P] [US1] Create Pydantic schemas for records (RecordCreate, RecordUpdate, RecordResponse, RecordListItem) in `backend/app/schemas/records.py`
- [ ] T030 [P] [US1] Create Pydantic schemas for media (MediaUploadResponse, MediaUpdate) in `backend/app/schemas/media.py`
- [ ] T031 [P] [US1] Create Pydantic schemas for text entries (TextEntryCreate, TextEntryUpdate) in `backend/app/schemas/text_entries.py`
- [ ] T032 [US1] Create media processor service with thumbnail generation (Pillow), HEIC conversion (pillow-heif), EXIF date extraction in `backend/app/services/media_processor.py`
- [ ] T033 [US1] Create records API router: POST /api/records, GET /api/records/{date}, PUT /api/records/{date}, DELETE /api/records/{date} in `backend/app/api/records.py`
- [ ] T034 [US1] Create media API router: POST /api/media/upload (with file validation, thumbnail generation, EXIF reading), GET /api/media/{id}/file, GET /api/media/{id}/thumbnail, PUT /api/media/{id}, DELETE /api/media/{id} in `backend/app/api/media.py`
- [ ] T035 [US1] Register records and media routers in FastAPI app in `backend/app/main.py`

### Frontend Implementation for US1

- [ ] T036 [P] [US1] Create records API client (createRecord, getRecord, updateRecord, deleteRecord) in `src/api/records.ts`
- [ ] T037 [P] [US1] Create media API client (uploadMedia, getMediaUrl, getThumbnailUrl, updateMedia, deleteMedia) in `src/api/media.ts`
- [ ] T038 [US1] Create records Pinia store (current record, CRUD actions, loading state) in `src/stores/records.ts`
- [ ] T039 [US1] Create MediaUploader component with drag-and-drop, file type validation, progress indicator in `src/components/media/MediaUploader.vue`
- [ ] T040 [US1] Create RecordEditView with date picker, text editor, media uploader, save/cancel buttons in `src/views/RecordEditView.vue`
- [ ] T041 [US1] Create basic TimelineView with day-level list showing records with first thumbnail and preview text in `src/views/TimelineView.vue`
- [ ] T042 [US1] Create AppHeader component with navigation and "添加记录" FAB button in `src/components/common/AppHeader.vue`
- [ ] T043 [US1] Create EmptyState component for no-records placeholder in `src/components/common/EmptyState.vue`

**Checkpoint**: User Story 1 fully functional — can create, view, and delete daily records with media

---

## Phase 4: User Story 2 — 时间轴浏览与筛选 (Priority: P2)

**Goal**: 用户能按日/周/月/年粒度浏览记录，在平铺和折叠视图间切换

**Independent Test**: 创建多日记录 → 切换日/周/月/年视图 → 验证聚合正确 → 切换平铺/折叠 → 验证展示变化

### Backend Implementation for US2

- [ ] T044 [US2] Extend records API: GET /api/records with view (day/week/month/year), date, page, page_size query params and aggregation logic in `backend/app/api/records.py`
- [ ] T044a [US2] Add keyword search (q param matching text_entries.content and media_entries.description) and date_from/date_to range filter to GET /api/records in `backend/app/api/records.py`

### Frontend Implementation for US2

- [ ] T045 [US2] Create TimelineFilter component with view granularity selector (日/周/月/年), layout toggle (平铺/折叠), keyword search input, and date range picker in `src/components/timeline/TimelineFilter.vue`
- [ ] T046 [US2] Create TimelineCard component for individual record card (thumbnail, date, entry count, preview text) in `src/components/timeline/TimelineCard.vue`
- [ ] T047 [US2] Create TimelineGroup component for aggregated views (week/month/year header with summary stats) in `src/components/timeline/TimelineGroup.vue`
- [ ] T048 [US2] Enhance TimelineView with multi-granularity support, flat/collapsed toggle, infinite scroll, drill-down navigation in `src/views/TimelineView.vue`
- [ ] T049 [US2] Update records Pinia store with view mode state, pagination, granularity switching, search query and date range in `src/stores/records.ts`

**Checkpoint**: User Stories 1 AND 2 both work independently — full timeline browsing operational

---

## Phase 5: User Story 3 — 里程碑标记 (Priority: P3)

**Goal**: 用户能将记录标记为里程碑，选择分类，在时间轴上醒目展示

**Independent Test**: 创建记录 → 标记为里程碑 (分类: 身体发育) → 时间轴显示里程碑图标 → 筛选仅显示里程碑

### Backend Implementation for US3

- [ ] T050 [P] [US3] Create Pydantic schemas for milestones (MilestoneCreate, MilestoneResponse, CategoryCreate, CategoryResponse) in `backend/app/schemas/milestones.py`
- [ ] T051 [US3] Create milestones API router: POST /api/milestones, DELETE /api/milestones/{id}, GET /api/milestone-categories, POST /api/milestone-categories in `backend/app/api/milestones.py`
- [ ] T052 [US3] Register milestones router in FastAPI app in `backend/app/main.py`
- [ ] T053 [US3] Extend GET /api/records to support milestone_only filter and return milestone info in `backend/app/api/records.py`

### Frontend Implementation for US3

- [ ] T054 [P] [US3] Create milestones API client (createMilestone, deleteMilestone, getCategories, createCategory) in `src/api/milestones.ts`
- [ ] T055 [US3] Create milestones Pinia store (categories, CRUD actions) in `src/stores/milestones.ts`
- [ ] T056 [US3] Create MilestoneMarker component (milestone icon badge, category label for timeline cards) in `src/components/timeline/MilestoneMarker.vue`
- [ ] T057 [US3] Create MilestonePicker dialog component (category selection, custom name input) in `src/components/record/MilestonePicker.vue`
- [ ] T058 [US3] Add milestone mark/unmark action to RecordDetailView in `src/views/RecordDetailView.vue`
- [ ] T059 [US3] Add milestone-only filter toggle to TimelineFilter and integrate with TimelineView in `src/components/timeline/TimelineFilter.vue`
- [ ] T060 [US3] Create MilestoneView with all milestones listed chronologically, grouped by category in `src/views/MilestoneView.vue`

**Checkpoint**: All milestones functional — create, display, filter

---

## Phase 6: User Story 4 — 日记式展示 (Priority: P4)

**Goal**: 记录以精美日记形式展示图文并茂内容，支持多主题风格

**Independent Test**: 创建含图片+配文的记录 → 打开详情 → 验证日记排版 → 切换主题 → 验证即时变化

### Frontend Implementation for US4

- [ ] T061 [US4] Create DiaryView component with magazine-style layout for single image + caption in `src/components/record/DiaryView.vue`
- [ ] T062 [US4] Create ImagePreview component with zoom, fullscreen, swipe gallery support in `src/components/media/ImagePreview.vue`
- [ ] T063 [US4] Create VideoPlayer component with inline playback and poster thumbnail in `src/components/media/VideoPlayer.vue`
- [ ] T064 [US4] Create RecordDetailView integrating DiaryView, ImagePreview, VideoPlayer with elegant typography in `src/views/RecordDetailView.vue`
- [ ] T065 [US4] Create ThemeSwitcher component with preview swatches for 3 themes + dark mode toggle in `src/components/common/ThemeSwitcher.vue`
- [ ] T066 [US4] Create settings Pinia store with theme/dark_mode state and persistence via Settings API in `src/stores/settings.ts`
- [ ] T067 [US4] Integrate ThemeSwitcher into AppHeader and apply data-theme attribute to document root in `src/App.vue`

**Checkpoint**: Full diary-style display with theme switching

---

## Phase 7: User Story 5 — 存储优化与数据管理 (Priority: P5)

**Goal**: 智能存储管理，存储统计，数据导出为 ZIP

**Independent Test**: 上传 100 张图片 → 检查 DB 大小 → 查看存储统计 → 执行导出 → 验证 ZIP 内容完整

### Backend Implementation for US5

- [ ] T068 [P] [US5] Create Pydantic schemas for export (ExportRequest, ExportStatus, StorageStats) in `backend/app/schemas/export.py`
- [ ] T069 [P] [US5] Create Pydantic schemas for settings (SettingsResponse, SettingsUpdate) in `backend/app/schemas/settings.py`
- [ ] T070 [US5] Create export service with async ZIP generation (metadata.json + media files + README.txt) in `backend/app/services/export_service.py`
- [ ] T071 [US5] Create export API router: POST /api/export, GET /api/export/status in `backend/app/api/export.py`
- [ ] T072 [US5] Create storage stats endpoint: GET /api/storage/stats in `backend/app/api/export.py`
- [ ] T073 [US5] Create settings API router: GET /api/settings, PUT /api/settings in `backend/app/api/settings.py`
- [ ] T074 [US5] Register export and settings routers in FastAPI app in `backend/app/main.py`

### Frontend Implementation for US5

- [ ] T075 [P] [US5] Create export API client (startExport, getExportStatus) and storage API client (getStorageStats) in `src/api/export.ts`
- [ ] T076 [P] [US5] Create settings API client (getSettings, updateSettings) in `src/api/settings.ts`
- [ ] T077 [US5] Create SettingsView with theme selection, dark mode toggle, storage stats display, export button with progress in `src/views/SettingsView.vue`

**Checkpoint**: All user stories independently functional

---

## Phase 8: User Story 6 — 成长曲线可视化 (Priority: P6)

**Goal**: 记录宝宝身高/体重等量化指标，以折线图展示成长趋势

**Independent Test**: 为多个日期添加身高/体重 → 打开成长曲线 → 验证折线图正确 → 点击数据点显示详情

### Backend Implementation for US6

- [ ] T087 [P] [US6] Create GrowthMetric SQLAlchemy model in `backend/app/models/growth_metric.py`
- [ ] T088 [P] [US6] Create Pydantic schemas for growth metrics (GrowthMetricCreate, GrowthMetricResponse, GrowthCurveData) in `backend/app/schemas/growth_metrics.py`
- [ ] T089 [US6] Create growth metrics API router: POST /api/growth-metrics, GET /api/growth-metrics (with metric_type and date range params), DELETE /api/growth-metrics/{id} in `backend/app/api/growth_metrics.py`
- [ ] T090 [US6] Register growth metrics router in FastAPI app in `backend/app/main.py`

### Frontend Implementation for US6

- [ ] T091 [P] [US6] Create growth metrics API client (addMetric, getMetrics, deleteMetric) in `src/api/growth-metrics.ts`
- [ ] T092 [US6] Create GrowthMetricInput component for adding height/weight data to a daily record in `src/components/record/GrowthMetricInput.vue`
- [ ] T093 [US6] Create GrowthCurveView with ECharts/Chart.js line chart for height and weight trends in `src/views/GrowthCurveView.vue`
- [ ] T094 [US6] Add growth curve route to vue-router and navigation entry in AppHeader in `src/router/index.ts`
- [ ] T095 [US6] Integrate GrowthMetricInput into RecordEditView for adding metrics during record creation in `src/views/RecordEditView.vue`

**Checkpoint**: Growth curve visualization fully functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T078 [P] Add auto-draft save for RecordEditView (localStorage fallback) in `src/views/RecordEditView.vue`
- [ ] T079 [P] Add broken media file detection with graceful placeholder display in `src/components/media/ImagePreview.vue` and `src/components/media/VideoPlayer.vue`
- [ ] T080 [P] Add file size validation (reject video > 2GB) with user-friendly error toast in `src/components/media/MediaUploader.vue`
- [ ] T081 [P] Add HEIC to JPEG auto-conversion for Windows compatibility in `backend/app/services/media_processor.py`
- [ ] T082 [P] Add loading skeletons and transition animations to TimelineView and RecordDetailView in `src/components/common/LoadingSkeleton.vue`
- [ ] T083 Optimize timeline query performance with pagination and thumbnail lazy loading in `src/views/TimelineView.vue`
- [ ] T084 Add global error handling with user-friendly toast notifications in `src/composables/useErrorHandler.ts`
- [ ] T085 Final UI polish — verify clean layout, consistent spacing, responsive behavior across all views
- [ ] T086 Run quickstart.md validation — verify dev setup, build, and package workflows end-to-end
- [ ] T096 [P] Add thumbnail cache cleanup service (clear oldest/least-accessed when exceeding threshold) in `backend/app/services/storage_manager.py`
- [ ] T097 [P] Add thumbnail cache stats and cleanup trigger button to SettingsView in `src/views/SettingsView.vue`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Phase 2
  - US2 (P2): Depends on US1's TimelineView (T041) existing
  - US3 (P3): Can start after Phase 2 (independent)
  - US4 (P4): Depends on US1's record creation flow
  - US5 (P5): Can start after Phase 2 (independent backend)
  - US6 (P6): Depends on US1's record creation flow (needs RecordEditView)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

```text
Phase 1 (Setup) → Phase 2 (Foundation)
                        ↓
              ┌─────────┼─────────┐
              ↓         ↓         ↓
           US1(P1)   US3(P3)   US5(P5)
              ↓
        ┌────┼────┐
        ↓    ↓    ↓
     US2(P2) US4(P4) US6(P6)
              ↓
        Phase 9 (Polish)
```

### Parallel Opportunities

**Phase 2 — Foundation** (8 parallel tasks):
```
T017, T018, T019, T020 — all SQLAlchemy models (different files)
T025, T026 — TypeScript types (different files)
T027 — CSS themes
T028 — Storage manager
```

**Phase 3 — US1** (5 parallel tasks):
```
T029, T030, T031 — Pydantic schemas (different files)
T036, T037 — API clients (different files)
```

**Phase 5 — US3** (2 parallel tasks):
```
T050, T054 — Milestone schemas + API client (different files)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Create a record with image + text, see it on timeline
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Create + view records (MVP!)
3. Add US2 → Timeline browsing with 4 granularities + 2 view modes
4. Add US3 → Milestone marking and filtering
5. Add US4 → Diary-style display + themes
6. Add US5 → Storage stats + data export
7. Add US6 → Growth curve visualization (height/weight trends)
8. Polish → Error handling, performance, UX refinements

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
