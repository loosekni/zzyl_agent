# zzyl_agent 接口文档

> 本目录是 zzyl_agent 服务的接口文档总入口。文档由 Codex 维护，代码由 Claude 维护。
> 编写规范见项目根目录 [`CODEX.md`](../../CODEX.md)。

## 1. 基本信息

| 项 | 值 |
|----|----|
| 服务名 | ZZYL Agent |
| Base URL | `http://localhost:8000` |
| 全局前缀 | `/api` |
| 健康检查 | `GET /health`（根级，无前缀） |
| OpenAPI（自动） | `GET /openapi.json` |
| Swagger UI | `GET /docs` |

> 全局前缀由 `settings.api_prefix` 控制，默认 `/api`。下文所有路径均已含前缀。

## 2. 接口分组

| 分组 | 前缀 | 源文件 | 文档 |
|------|------|--------|------|
| Agent 工作流 | `/api/agent` | `backend/app/api/agent.py` | [`agent.md`](./agent.md) |
| Nursing 业务 | `/api/nursing` | `backend/app/api/nursing.py` | [`nursing.md`](./nursing.md) |

## 3. 通用约定

### 3.1 请求

- `GET` 请求参数走 query string；`POST`/`PUT`/`DELETE` 请求体为 `application/json`。
- 字符串字段长度校验、枚举取值等约束来自代码中的 `Field(...)` 与 `StrEnum`，文档需如实记录。

### 3.2 通用错误响应

FastAPI 校验失败默认返回 422，结构如下（其它错误码见 [`errors.md`](./errors.md)）：

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "elder_name"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

### 3.3 枚举值速查

| 枚举 | 取值 | 说明 |
|------|------|------|
| `Gender` | `male` / `female` / `unknown` | 性别 |
| `BedStatus` | `available` / `occupied` / `maintenance` | 床位状态 |
| `AlertSeverity` | `low` / `medium` / `high` / `critical` | 告警级别 |
| `CheckInStatus` | `draft` / `reviewing` / `approved` / `rejected` | 入住申请状态 |

## 4. 接口清单（待 Codex 逐个填充）

> 以下清单基于当前代码梳理，✅=已落地的接口，🔜=规划中。每完成一个接口文档，在对应文件里按 [`CODEX.md`](../../CODEX.md) 的模板填写。

### Agent 工作流（`docs/api/agent.md`）

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | `/api/agent/health` | agent 模块健康检查 | ✅ |
| POST | `/api/agent/chat` | 通用对话 | ✅ |
| POST | `/api/agent/checkin/recommendation` | 入住推荐建议 | ✅ |
| POST | `/api/agent/care-plan` | 生成护理计划 | ✅ |
| POST | `/api/agent/alert-analysis` | 告警分析 | ✅ |
| POST | `/api/agent/health-profile` | 老人健康风险画像 | ✅ |
| POST | `/api/agent/admission/preview` | 入住办理预览（reservation token） | ✅ |
| POST | `/api/agent/admission/confirm` | 入住办理确认 | ✅ |
| POST | `/api/agent/admission/cancel` | 入住办理取消 | ✅ |
| POST | `/api/agent/chat/stream` | 对话流式输出（SSE） | 🔜 待开发 |
| POST | `/api/agent/care-plan/stream` | 护理计划流式输出 | 🔜 待开发 |

### Nursing 业务（`docs/api/nursing.md`）

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | `/api/nursing/elders` | 老人列表 | ✅ |
| POST | `/api/nursing/elders` | 新建老人 | ✅ |
| GET | `/api/nursing/rooms` | 房间列表 | ✅ |
| POST | `/api/nursing/rooms` | 新建房间 | ✅ |
| GET | `/api/nursing/beds` | 床位列表 | ✅ |
| POST | `/api/nursing/beds` | 新建床位 | ✅ |
| GET | `/api/nursing/projects` | 护理项目列表 | ✅ |
| POST | `/api/nursing/projects` | 新建护理项目 | ✅ |
| GET | `/api/nursing/alerts` | 告警列表 | ✅ |
| POST | `/api/nursing/alerts` | 新建告警 | ✅ |
| GET | `/api/nursing/checkins` | 入住申请列表 | ✅ |
| POST | `/api/nursing/checkins` | 新建入住申请 | ✅ |
| POST | `/api/nursing/demo/seed` | 灌入演示数据 | ✅ |

## 5. 文档编写规范（摘要）

完整规范见 [`CODEX.md`](../../CODEX.md)。每个接口必须包含：

1. 方法 + 路径 + 描述 + 标签
2. 请求参数表（字段 / 类型 / 必填 / 默认 / 校验规则 / 说明）
3. 请求示例（可执行 JSON）
4. 响应结构表 + 响应示例
5. 错误码表（HTTP / 含义 / 触发场景）
6. 业务备注

> **铁律**：文档字段以代码 `schemas/` 与 `models/` 为准，不臆造。代码缺描述时文档标 `待补充` 并提示 Claude 补 docstring。
