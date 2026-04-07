# API Contract: Records — Phase 3 (Allergy & Date)

基路径假定与现有应用一致：`/api/records`（前缀以实现为准）。所有需登录路由携带现有 `Authorization`。

## 字段变更（JSON）

### RecordCreate / RecordUpdate / RecordResponse / RecordListItem

新增可选/必选字段（实现时与 Pydantic 对齐）：

| 字段名（建议） | 类型 | 说明 |
|----------------|------|------|
| `allergy_notes` | `string \| null` | 宝宝过敏食物说明；空白应视为无 |

### 日期规则

- `date`（`YYYY-MM-DD`）：**不得晚于** 服务端校验时使用的「今天」（与嵌入后端同机本地日一致）。
- 违规响应：`422` 或 `400`，`detail` 含可读中文或结构化错误码。

## 端点

### A. 扩展现有列表（推荐）

`GET /api/records`

Query（新增，可选）：

| 参数 | 类型 | 说明 |
|------|------|------|
| `has_allergy` | `boolean` | `true` 时仅返回 `allergy_notes` 非空记录 |

行为：与现有分页、认证、过滤兼容；响应项中含 `allergy_notes`（或列表精简为摘要，以实现为准，但需满足 spec「全部可查」）。

### B. 备用专用列表

若无法与现有查询组合：

`GET /api/records/allergies`

- **200**：`{ "items": [ { "date": "...", "allergy_notes": "...", ... } ] }`
- 认证与同用户隔离与现有 records 一致。

## 错误示例（说明性）

```json
{
  "detail": "记录日期不能晚于今天"
}
```

（具体字段以 FastAPI `HTTPException` / `ValidationError` 包装为准。）
