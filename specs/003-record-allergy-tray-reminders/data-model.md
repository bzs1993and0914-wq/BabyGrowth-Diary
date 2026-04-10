# Data Model: 003-record-allergy-tray-reminders

## Entity: DailyRecord（扩展）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `allergy_notes`（建议名，以实现为准） | `TEXT`，可空 | 默认 `NULL` | 宝宝过敏食物自由文本；仅空白/null 视作「无过敏信息」 |

**校验（业务层）**:

- `date`：提交值必须 **≤ 当前机器本地日历日**（ISO `YYYY-MM-DD` 字符串比较或与 `date.today()` 一致）。
- `allergy_notes`：可选；若仅空格应规范化为 `NULL` 或空串不参与「含过敏」过滤（与 spec 边件一致）。

**关系**: 与现有一致：`MediaEntry`、`TextEntry` 等仍 `daily_record_id` → `daily_records.id`。

## 逻辑视图: 过敏聚合列表

非持久化表；查询定义为：

- 过滤：`allergy_notes IS NOT NULL AND trim(allergy_notes) != ''`
- 排序：按 `date` 降序（与用户查阅「最近优先」一致）
- 投影：至少包含 `date`、`allergy_notes`、便于跳转详情的 `id` 或 `date` 键

## 客户端持久化: 提醒去重（非 SQLite）

| 键 | 类型 | 说明 |
|----|------|------|
| `lastDailyRecordNudgeDate` | `string` (`YYYY-MM-DD`) | 已在该本地日展示过 10:00 提醒则不再重复 |

存储位置：Electron `userData`（如 `electron-store` JSON），**不**进入共享 SQLite，避免与多账户/备份策略耦合；若未来需同步再评估。

## 状态: 主窗口 / 托盘

运行时状态，不持久化：`BrowserWindow` 可见性、`Tray` 实例引用。
