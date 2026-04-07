# Phase 0 — Research: 003-record-allergy-tray-reminders

## R-001 — 过敏数据建模

- **Decision**: 在 `daily_records` 表增加可空文本列（建议字段名 `allergy_notes` 或 `baby_allergy_foods`），与现有「每用户每日期一条记录」模型一致；不以独立 `allergy_events` 表为 MVP。
- **Rationale**: 规格假设单输入框、按「非空即参与聚合」过滤；一列即可满足 FR，且与当前 `DailyRecord` 中心模型一致，迁移成本最低。
- **Alternatives considered**: 子表多行过敏原——更利于结构化统计，但超出 spec 的单一文本框描述，属 YAGNI。

## R-002 — 过敏记录列表 API 形态

- **Decision**: 优先实现 `GET /api/records?has_allergy=true`（或与现有列表参数风格一致的查询开关），返回现有列表项 DTO 并含过敏摘要字段；若与现有分页/过滤冲突，则新增 `GET /api/records/allergies` 返回精简列表（日期 + 预览文本）。
- **Rationale**: 复用认证与序列化逻辑；首页仅需只读聚合。
- **Alternatives considered**: 仅前端拉全量再过滤——数据量大时浪费带宽，违背简洁与性能预期。

## R-003 — 「今天」边界与校验

- **Decision**: 「今天」定义为服务器进程所在机器的本地日期（与 SQLite 同一主机，即桌面场景下与用户本机一致）。后端在 create/update/含改日期的操作中使用 `date.today().isoformat()`（或等价）比较请求体中的 `date` 字符串；前端 DatePicker `disabled-date` 禁用未来日。
- **Rationale**: 双端校验防绕过；嵌入式后端与用户同机，时区一致风险低。
- **Alternatives considered**: 仅以服务端 UTC 换算——在跨时区单机场景几乎不必要，且增加与用户日历心智不一致风险。

## R-004 — 每日 17:00 提醒实现

- **Decision**: 在 Electron **主进程**用 `setInterval`（如每 60s）或下一次 `setTimeout` 对齐到本地 17:00，触发 `Notification`（或 `dialog.showMessageBox` 降级）；将「已提醒日期」存 `electron-store` 键如 `lastDailyRecordNudgeDate`（`YYYY-MM-DD`），自然日维度去重。
- **Rationale**: 规格要求客户端侧、本地时区、每自然日最多一次；无需后端参与，符合离线优先。
- **Alternatives considered**: `node-cron`——依赖更小可不用；系统日历/launchd——过重。

## R-005613 — 关闭窗口 → 托盘

- **Decision**: `BrowserWindow` 的 `close` 事件中 `preventDefault()`，`mainWindow.hide()`；`new Tray(icon)`，`tray.on('click')` 时 `show()` + `focus()`；`contextMenu` 含「退出」调用 `app.quit()` 并链式 `stopPythonBackend`（与现有生命周期一致）。
- **Rationale**: Electron 官方模式；满足 FR-006/FR-007。
- **Alternatives considered**: 最小化到 Dock/任务栏而不设 Tray——不满足「小图标挂在托盘」的产品描述。

## R-006 — 托盘图标不可用降级

- **Decision**: 若 `Tray` 构造失败（极少见），记录日志并回退为：关闭窗口改为最小化（`minimize`）并依赖 Dock/任务栏图标恢复；仍提供菜单栏或应用内「退出」。
- **Rationale**: 对齐 spec 边界情况，避免无窗且不可恢复进程。

## R-005 typo fix

I had R-005613 by mistake - fix research.md to R-005 for tray - I'll fix the header "## R-005613" -> remove duplicate, use R-005 and R-006 only once. Let me read the file and fix.

Actually I'll fix: change R-005613 to R-005 and the next R-006 about 托盘降级 - merge or renumber.

I'll rewrite research.md cleanly without typo.
</think>


<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
StrReplace