# Implementation Plan: Phase Three — Record Date Cap, Allergy, Reminder, Tray

**Branch**: `003-record-allergy-tray-reminders` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/003-record-allergy-tray-reminders/spec.md`

## Summary

在现有 **Electron + Vue 3 + FastAPI + SQLAlchemy/SQLite** 架构上交付阶段三能力：（1）创建/编辑记录时日期不得超过本地「今天」，前后端双重校验；（2）每日记录增加「宝宝过敏食物」文本字段，首页入口进入聚合列表，时间轴/记录列表醒目标识；（3）桌面应用在每个自然日本地 10:00 至多一次系统通知式提醒（文案固定含义）；（4）关闭主窗口时隐藏窗口并驻留系统托盘，点击托盘图标恢复主窗口，托盘菜单提供「退出」以结束进程。

技术路径概要：SQLite 新增列 + Pydantic 与 records API 扩展；可选专用列表端点或复用带查询参数的列表接口；Vue 侧日期控件、`RecordEditView`/`Timeline` 样式与首页路由；Electron `Tray` + `on('close')` 拦截 + 计划任务（`setTimeout` 链或轻量调度）+ `electron-store` 或等价持久化存储「上次提醒自然日」。

## Technical Context

**Language/Version**: Python 3.11+（后端）、TypeScript 5.x（前端/Electron 主进程）  
**Primary Dependencies**: FastAPI 0.115+、SQLAlchemy 2.0、Pydantic v2、Electron 33+、Vue 3.5+、Element Plus 2.9+、Pinia 2.x、Vite  
**Storage**: SQLite（结构化数据）；用户偏好/提醒去重可存本地 JSON（`electron-store` 或 `app.getPath('userData')` 下文件）  
**Testing**: pytest（后端路由与校验）；前端关键逻辑可用 Vitest 或人工验收清单（见 quickstart）  
**Target Platform**: macOS（优先）、Windows 桌面  
**Project Type**: 桌面应用（Electron）+ 本地嵌入式 FastAPI 服务  
**Performance Goals**: 列表与过敏聚合查询在常规数据量下单次响应保持既有水平（约 200ms 以内本地）；提醒调度不阻塞主线程 UI  
**Constraints**: 宪法要求离线优先、数据不出本地；提醒仅在应用进程存活且 OS 允许通知时有效（与 spec Assumptions 一致）  
**Scale/Scope**: 单用户/少量用户本地库；新增 1 列 + 1～2 个 API 形态 + Electron 托盘与定时逻辑  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原则 | 评估 |
|------|------|
| I 用户体验优先 | 通过：过敏高对比展示、日期错误可理解提示、托盘一键恢复；退出路径明确。 |
| II 数据安全与隐私 | 通过：过敏与提醒状态均留在本机；无遥测。 |
| III 离线优先 | 通过：记录与过敏读写不依赖外网。提醒依赖本机时钟与应用运行，已在 spec 假设中说明。 |
| IV 时间轴驱动 | 通过：过敏聚合仍以记录日期为主轴展示。 |
| V 媒体丰富性 | 与本特性无冲突。 |
| VI 简洁至上 | 通过：过敏用单列文本而非新表（除非后续要结构化过敏原编码）。 |

**Post-Phase 1**：契约与数据模型未引入违反宪法的复杂层；无需填写 Complexity Tracking。

## Project Structure

### Documentation (this feature)

```text
specs/003-record-allergy-tray-reminders/
├── plan.md           # 本文件
├── research.md       # Phase 0
├── data-model.md     # Phase 1
├── quickstart.md     # Phase 1
├── contracts/        # Phase 1
│   └── records-phase-3.md
├── spec.md
└── tasks.md          # /speckit.tasks（本命令不生成）
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/records.py          # 日期校验；过敏字段；可选 allergy 列表端点
│   ├── models/daily_record.py  # 新增 allergy_notes 列（命名以 tasks 为准）
│   ├── schemas/records.py       # Create/Update/Response 扩展
│   └── database/schema_upgrade.py  # SQLite ALTER（若项目沿用该模式）

electron/
└── main.ts                     # Tray、window close 行为、调度与本地提醒状态

src/
├── views/                      # 首页入口、过敏列表页、RecordEditView 表单项
├── components/timeline/        # 列表行样式（过敏警示）
├── types/api.ts                # 类型同步
└── router/                     # 新路由

public/ 或 build 资源            # 托盘图标（可用现有 app icon）
```

**Structure Decision**: 沿用仓库既有「`backend/` + `src/` + `electron/`」桌面应用布局；本特性不新增独立微服务或移动端工程。

## Complexity Tracking

> 无宪法违规项需特批；本节留空。

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
