# Implementation Plan: 002 账号体系、VIP 多图与上传失败默认图

**Branch**: `002-auth-vip-media-upload` | **Date**: 2026-03-25 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-auth-vip-media-upload/spec.md`

## Summary

在现有 Electron + Vue + FastAPI + SQLite 桌面应用上迭代：修复/兜底的媒体上传体验（无成功照片时的默认成长曲线配图）、本地账号注册/登录/修改密码、账户等级（普通 vs VIP）及对应单次上传张数上限（1 vs 9），并在详情/日记视图中按张数自适应排版。

## Technical Context

继承 [`specs/001-baby-growth-timeline/plan.md`](../001-baby-growth-timeline/plan.md) 中的技术栈与仓库结构；本特性新增关注点：

- **认证**: 用户名/邮箱 + 密码；本地 JWT 或等价会话令牌；密码哈希（如 bcrypt/argon2）。
- **授权**: 受保护 REST 路由；前端 axios 携带 `Authorization`。
- **账户等级**: 用户维度 `normal` | `vip`；上传接口与编辑页控件双重校验张数上限。
- **默认图**: 静态资源（打包进 `public/` 或 `src/assets/`），记录上可选布尔/枚举以区分「用户曾尝试上传但全部失败」与「从未选图」（按 spec 与产品约定实现）。

## Project Structure (this feature)

```text
specs/002-auth-vip-media-upload/
├── plan.md              # This file
├── spec.md
└── tasks.md             # /speckit.tasks output
```

代码变更主要涉及：

- `backend/app/models/` — `User`；`DailyRecord` 扩展（用户关联、默认图展示语义）。
- `backend/app/api/` — `auth.py` 新建；`deps.py` 依赖；`media.py` / `records.py` 接入认证与配额。
- `src/api/` — `auth.ts`；`client.ts` 拦截器。
- `src/stores/` — `auth.ts`。
- `src/views/` — 登录/注册页；设置内改密；路由守卫。
- `src/components/record/DiaryView.vue` — 默认图与多图排版。
- `src/components/media/MediaUploader.vue` — 失败处理与张数上限。

## Complexity / Notes

- 现有库使用 `create_all` 初始化；若需兼容已有 SQLite 文件，需显式迁移步骤（`ALTER TABLE` 或一次性迁移脚本），见 `tasks.md` 中对应任务。
- 单用户桌面场景向「多账户」演进时，需将 `daily_records` 等与 `user_id` 关联；任务中已包含模型层准备。
