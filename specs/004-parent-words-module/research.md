# Phase 0 — Research: 004-parent-words-module

## R-001 — ParentWord 数据建模策略

- **Decision**: 新建独立的 `parent_words` 表，与 `daily_records` 表并行，共享 `user_id` 外键到 `users` 表。不复用或扩展 `daily_records`。
- **Rationale**: `DailyRecord` 以"用户+日期"为唯一约束，与"父母心语"的按条记录、不绑定日期的需求本质不同。独立表避免概念混淆，利于各自独立演化（如心语未来支持时间胶囊、标签等）。
- **Alternatives considered**: 
  - 扩展 `DailyRecord` 增加类型字段——混淆"每日记录"与"心语"两种不同粒度的概念，查询逻辑复杂化。
  - 通用"文章"表——过度抽象，当前仅有两种内容类型，引入多态增加复杂度。

## R-002 — 媒体附件关联方式

- **Decision**: 在 `media_entries` 表新增可空列 `parent_word_id`（`ForeignKey → parent_words.id, ON DELETE CASCADE`），与已有 `daily_record_id` 互斥——每条 media 要么属于 DailyRecord，要么属于 ParentWord。上传接口接受 `parent_word_id` 参数（与 `daily_record_id` 二选一）。
- **Rationale**: 复用现有 `MediaEntry` 模型和上传/下载/缩略图管道，改动最小。`parent_word_id` 为可空 + `ON DELETE CASCADE`，新列不影响现有记录。互斥约束在应用层校验（非数据库 CHECK，因 SQLite 对复合 CHECK 支持有限且项目沿用应用层校验风格）。
- **Alternatives considered**:
  - 独立的 `parent_word_media` 表——完全解耦，但需复制整套上传/下载/缩略图逻辑或引入多态服务层，开发成本高。
  - 通用多态关联 (`content_type` + `content_id`)——灵活但增加查询复杂度、丧失外键约束保护。

## R-003 — 用户角色 (parent_role) 存储位置

- **Decision**: 在 `users` 表新增 `parent_role` 列（`TEXT, nullable`），值域为 `dad`/`mom`/`NULL`。通过现有 `/api/auth/me` 返回，通过新增 `/api/auth/profile` 或扩展 settings API 更新。
- **Rationale**: `parent_role` 是用户属性而非应用全局设置，放在 `users` 表语义最准确。当前 `AppSettings` 是全局键值表（非 per-user），不适合存储。直接加在 `User` 模型上，`/api/auth/me` 已有现成的序列化通道。
- **Alternatives considered**:
  - `AppSettings` 键值存储——不是 per-user 的，多用户场景（如爸爸妈妈分别注册）会冲突。
  - 新建 `user_preferences` 表——在只需要一个字段时过度设计。

## R-004 — 导航嵌套分组交互方案（PC 端）

- **Decision**: PC 端采用"点击/悬停展开下拉面板"模式。「宝宝成长」显示为一个带下拉箭头的导航项，hover 或 click 展开包含三个子项的面板；「父母有话说」为直接可点击的独立导航项。当子项被选中时，父级「宝宝成长」保持高亮。
- **Rationale**: 下拉面板是 Web 应用最常见的分组导航模式，Element Plus 的 `el-popover` 或纯 CSS `:hover` 面板即可实现，无需引入新组件库。用户只需一次 hover/click 即可看到所有子项，满足 SC-004（≤2 次点击可达）。
- **Alternatives considered**:
  - Tab + 子 Tab 二级栏——占用纵向空间，与现有 60px 高度 header 布局冲突。
  - Sidebar 侧边栏——对桌面应用偏重，且现有布局无侧栏基础。

## R-005 — 导航嵌套分组交互方案（移动端）

- **Decision**: 移动端底部抽屉中以"分区标题 + 子项列表"形式呈现。「宝宝成长」作为灰色小标题/分隔符，下方列出时间轴/里程碑/成长曲线三个可点击项；然后是一个分隔线，再是「父母有话说」作为独立可点击项。
- **Rationale**: 移动端抽屉空间充裕（已有 `min(78vh, 520px)` 高度），分区标题 + 平铺子项是最清晰的移动端分组模式，无需折叠/展开交互。
- **Alternatives considered**:
  - Accordion 折叠组——移动端分组折叠增加操作步骤，仅 4 个导航项不值得折叠。

## R-006 — 全屏编辑页面路由设计

- **Decision**: 新增 3 条路由：`/parent-words`（列表）、`/parent-words/new`（新建）、`/parent-words/:id/edit`（编辑）、`/parent-words/:id`（详情）。编辑和新建共用一个 `ParentWordEditView.vue`，通过路由参数区分模式（参照现有 `RecordEditView.vue` 的 `isNew` 逻辑）。
- **Rationale**: 与现有 `/record/*` 路由设计风格一致；独立路由保证浏览器前进/后退正常；编辑页为全屏沉浸式写作体验。
- **Alternatives considered**: 弹窗/抽屉编辑——用户选择了全屏页面方案（clarify Q3: A），因长文写作需要充足空间。

## R-007 — 草稿自动保存策略

- **Decision**: 使用 `localStorage` 存储编辑中的草稿，键为 `parent-word-draft-{id|new}`，值为 JSON `{ title, content, authorRole, timestamp }`。每 30 秒或内容变化时（debounce 2s）自动保存。成功提交后删除对应草稿。进入编辑页时检测是否有未保存草稿并提示恢复。
- **Rationale**: `localStorage` 零依赖、离线可用、与现有客户端持久化模式一致。30 秒间隔 + debounce 平衡了保存频率和性能。不使用 `IndexedDB` 因为内容量小（文本 + 少量元数据），`localStorage` 足够。
- **Alternatives considered**:
  - `electron-store` 主进程存储——需 IPC 通信，增加复杂度，且当前特性是 Web 渲染进程功能。
  - 后端草稿 API——增加后端复杂度，离线场景可能不可用。

## R-008 — 标签功能（P3 延后）

- **Decision**: P3 标签功能不在本期实现。数据模型中预留 `parent_word_tags` 和 `parent_word_tag_associations` 表的概念设计，但不建表、不建 API。`ParentWord` 模型中不预设 tags 关系字段。
- **Rationale**: 规格明确标签为 P3 优先级，核心功能先稳定。过早建表可能因需求细化而变更，增加迁移负担。
- **Alternatives considered**: 预建空表——违背 YAGNI 原则，且 SQLite ALTER TABLE 在后续添加时成本极低。
