# Agent 工作流接口文档

> 源文件：backend/app/api/agent.py
> 请求/响应模型：backend/app/schemas/agent.py
> 枚举与表模型：backend/app/models/nursing.py

本文件覆盖 `/api/agent/*` 全部接口，按 [`CODEX.md`](../../CODEX.md) 模板编写。全局前缀 `/api`，路由器前缀 `/agent`，标签 `agent`。

---

## 接口清单

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | `/api/agent/health` | agent 模块健康检查 | ✅ |
| POST | `/api/agent/chat` | 通用对话 | ✅ |
| POST | `/api/agent/checkin/recommendation` | 入住推荐建议 | ✅ |
| POST | `/api/agent/care-plan` | 生成护理计划 | ✅ |
| POST | `/api/agent/alert-analysis` | 告警分析 | ✅ |
| POST | `/api/agent/health-profile` | 老人健康风险画像 | ✅ |
| POST | `/api/agent/admission/preview` | 入住办理预览（生成 reservation token） | ✅ |
| POST | `/api/agent/admission/confirm` | 入住办理确认 | ✅ |
| POST | `/api/agent/admission/cancel` | 入住办理取消 | ✅ |
| POST | `/api/agent/chat/stream` | 对话流式输出（SSE） | 🔜 待开发 |
| POST | `/api/agent/care-plan/stream` | 护理计划流式输出 | 🔜 待开发 |

### AdmissionStatus 枚举（入住办理状态机）

入住办理相关接口的 `status` 字段取值来自 `models/nursing.py` 的 `AdmissionStatus`：

| 取值 | 说明 |
|------|------|
| `IDLE` | 空闲（初始） |
| `RUNNING` | 办理中 |
| `WAITING_APPROVAL` | 待人工确认（preview 成功后的状态，持有 reservation_token） |
| `COMPLETED` | 已确认入住（confirm 成功） |
| `CANCELLED` | 已取消（cancel 成功） |
| `EXPIRED` | 已过期（token 超过 15 分钟未确认） |
| `FAILED` | 失败 |

---

## 1. agent 模块健康检查

- **方法**：`GET`
- **路径**：`/api/agent/health`
- **描述**：检查 agent 模块是否可用，返回固定存活探针。无需任何入参，常用于 K8s/网关 liveness 探测。
- **标签**：agent

#### 请求参数

无（既无 query 也无 body）。

#### 请求示例

```bash
curl -X GET http://localhost:8000/api/agent/health
```

#### 响应

##### 200 成功（application/json）

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 固定值 `ok`，表示 agent 路由器已挂载 |

##### 响应示例

```json
{
  "status": "ok"
}
```

#### 错误码

| HTTP | 含义 | 触发场景 |
|------|------|----------|
| 500 | 服务端错误 | 路由器未挂载或服务未启动（此时不会到达该接口） |

#### 业务备注

- 该接口不依赖数据库或 LLM，仅用于探活。
- 根级健康检查为 `GET /health`（无 `/api` 前缀），与本接口职责区分：根级代表整服务，本接口代表 agent 模块。

---

## 2. 通用对话

- **方法**：`POST`
- **路径**：`/api/agent/chat`
- **描述**：基于 LangGraph 构建的通用对话接口，将用户消息送入 chat graph，由 LLM 生成回复后同步返回。
- **标签**：agent

#### 请求参数

##### Body（application/json）

| 字段 | 类型 | 必填 | 默认值 | 校验规则 | 说明 |
|------|------|------|--------|----------|------|
| message | string | 是 | - | 1~4000 字符 | 用户输入的对话内容 |
| conversation_id | string | 否 | null | - | 会话 ID，用于上下文追踪；当前实现原样回传，不做多轮拼接 |

##### 请求示例

```json
{
  "message": "帮我介绍一下张桂兰老人最近的护理要点",
  "conversation_id": "conv-20260716-001"
}
```

#### 响应

##### 200 成功（application/json）

| 字段 | 类型 | 说明 |
|------|------|------|
| answer | string | LLM 生成的回复文本 |
| conversation_id | string \| null | 原样回传的会话 ID；请求未传则为 null |

##### 响应示例

```json
{
  "answer": "张桂兰老人近期需重点关注夜间血压波动与跌倒风险……",
  "conversation_id": "conv-20260716-001"
}
```

#### 错误码

| HTTP | 含义 | 触发场景 |
|------|------|----------|
| 422 | 参数校验失败 | `message` 为空或超过 4000 字符 |
| 500 | 服务端错误 | LLM 调用失败（待补全局异常处理） |

#### 业务备注

- 当前为同步返回，多轮上下文拼接由前端基于 `conversation_id` 维护。
- 流式版本规划为 `POST /api/agent/chat/stream`（SSE），🔜 待开发。
- `conversation_id` 当前不参与 graph 状态，仅作透传标识。

---

## 3. 入住推荐建议

- **方法**：`POST`
- **路径**：`/api/agent/checkin/recommendation`
- **描述**：根据老人姓名匹配档案，结合数据库中房间、床位、护理项目信息，由 LLM 生成入住推荐建议。
- **标签**：agent

#### 请求参数

##### Body（application/json）

| 字段 | 类型 | 必填 | 默认值 | 校验规则 | 说明 |
|------|------|------|--------|----------|------|
| elder_name | string | 是 | - | 1~64 字符 | 老人姓名，用于匹配老人档案；匹配不到时由 LLM 在 `suggestion` 中给出未找到提示 |

##### 请求示例

```json
{
  "elder_name": "张桂兰"
}
```

#### 响应

##### 200 成功（application/json）

| 字段 | 类型 | 说明 |
|------|------|------|
| elder_name | string | 老人姓名（原样回传） |
| suggestion | string | LLM 生成的入住推荐建议文本 |

##### 响应示例

```json
{
  "elder_name": "张桂兰",
  "suggestion": "建议安排朝南三人房，搭配跌倒预防与血压监测护理项目……"
}
```

#### 错误码

| HTTP | 含义 | 触发场景 |
|------|------|----------|
| 422 | 参数校验失败 | `elder_name` 为空或超过 64 字符 |
| 500 | 服务端错误 | LLM 调用失败（待补全局异常处理） |

#### 业务备注

- 当老人不存在时，接口不会 404，而是由 LLM 在 `suggestion` 中返回"未找到老人 X"之类的提示文本。
- 该接口仅生成建议，不写入任何数据库记录；正式办理请走 `/api/agent/admission/*` 闭环。

---

## 4. 生成护理计划

- **方法**：`POST`
- **路径**：`/api/agent/care-plan`
- **描述**：根据老人姓名与护理目标，结合档案与告警历史，由 LLM 生成结构化护理计划文本。
- **标签**：agent

#### 请求参数

##### Body（application/json）

| 字段 | 类型 | 必填 | 默认值 | 校验规则 | 说明 |
|------|------|------|--------|----------|------|
| elder_name | string | 是 | - | 1~64 字符 | 老人姓名，用于匹配老人档案 |
| care_goal | string | 否 | `""` | 最长 1000 字符 | 护理目标，为空时按"维持日常照护安全和舒适"处理 |

##### 请求示例

```json
{
  "elder_name": "张桂兰",
  "care_goal": "控制血压，降低夜间跌倒风险"
}
```

#### 响应

##### 200 成功（application/json）

| 字段 | 类型 | 说明 |
|------|------|------|
| elder_name | string | 老人姓名（原样回传） |
| care_goal | string | 护理目标（原样回传） |
| plan | string | LLM 生成的护理计划文本，通常包含护理重点、建议项目、执行频次、风险提醒 |

##### 响应示例

```json
{
  "elder_name": "张桂兰",
  "care_goal": "控制血压，降低夜间跌倒风险",
  "plan": "护理重点：夜间血压监测与跌倒预防。\n建议项目：血压监测、夜间巡视、跌倒预防护理。\n执行频次：血压监测每日 2 次，夜间巡视每 2 小时一次。\n风险提醒：注意低血压导致的头晕。"
}
```

#### 错误码

| HTTP | 含义 | 触发场景 |
|------|------|----------|
| 422 | 参数校验失败 | `elder_name` 为空/超长，或 `care_goal` 超过 1000 字符 |
| 500 | 服务端错误 | LLM 调用失败（待补全局异常处理） |

#### 业务备注

- 当老人不存在时，`plan` 字段返回"未找到老人 X 的档案"类似提示，不抛 404。
- 流式版本规划为 `POST /api/agent/care-plan/stream`，🔜 待开发。
- `care_goal` 为空字符串时由 LLM 自行按默认目标生成，业务层不强制替换。

---

## 5. 告警分析

- **方法**：`POST`
- **路径**：`/api/agent/alert-analysis`
- **描述**：根据告警 ID 加载告警记录及关联老人档案，由 LLM 生成告警原因分析与处置建议。
- **标签**：agent

#### 请求参数

##### Body（application/json）

| 字段 | 类型 | 必填 | 默认值 | 校验规则 | 说明 |
|------|------|------|--------|----------|------|
| alert_id | integer | 是 | - | > 0 | 告警记录 ID，对应 `AlertRecord.id` |

##### 请求示例

```json
{
  "alert_id": 12
}
```

#### 响应

##### 200 成功（application/json）

| 字段 | 类型 | 说明 |
|------|------|------|
| alert_id | integer | 告警 ID（原样回传） |
| analysis | string | LLM 生成的告警分析文本，通常包含原因推测、风险等级、处置建议 |

##### 响应示例

```json
{
  "alert_id": 12,
  "analysis": "该告警来自夜间床垫传感器，老人离床超过 15 分钟未归，结合历史可能有跌倒风险。建议值班护理员立即巡视，并核查老人意识与步态。"
}
```

#### 错误码

| HTTP | 含义 | 触发场景 |
|------|------|----------|
| 422 | 参数校验失败 | `alert_id` 缺失或 ≤ 0 |
| 500 | 服务端错误 | LLM 调用失败（待补全局异常处理） |

#### 业务备注

- 当前实现不校验 `alert_id` 是否存在，若不存在由 LLM 在 `analysis` 中给出"未找到告警"类似提示（待 Claude 在 graph 节点中明确）。
- 告警级别枚举 `AlertSeverity`：`low` / `medium` / `high` / `critical`，由 `/api/nursing/alerts` 写入。

---

## 6. 老人健康风险画像

- **方法**：`POST`
- **路径**：`/api/agent/health-profile`
- **描述**：根据老人 ID 采集档案与告警记录，计算风险评分与等级，推荐护理项目并生成结构化画像。多节点编排：collect（采集档案与告警）→ score（计算风险评分）→ recommend（推荐护理项目并生成总结）。当前为纯数据驱动，LLM 入口预留用于后续增强 `summary`。
- **标签**：agent

#### 请求参数

##### Body（application/json）

| 字段 | 类型 | 必填 | 默认值 | 校验规则 | 说明 |
|------|------|------|--------|----------|------|
| elder_id | integer | 是 | - | > 0 | 老人 ID，对应 `Elder.id` |

##### 请求示例

```json
{
  "elder_id": 3
}
```

#### 响应

##### 200 成功（application/json）

顶层字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| elder_id | integer | 老人 ID（原样回传） |
| elder_name | string | 老人姓名；未找到老人时为空字符串 `""` |
| health_summary | string | 老人健康摘要，来自 `Elder.health_summary`；为空时返回 `"无"`；未找到老人时返回 `"未找到该老人档案。"` |
| alert_total | integer | 该老人累计告警条数 |
| alert_stats | array&lt;object&gt; | 按告警级别聚合的统计列表，按 severity 由重到轻排序 |
| recent_alerts | array&lt;object&gt; | 最近 5 条告警，按 `created_at` 倒序 |
| top_devices | array&lt;object&gt; | 告警次数 Top 3 的设备列表 |
| risk_score | integer | 风险评分，0~100（按告警级别加权累加后封顶 100） |
| risk_level | string | 风险等级，取值 `低` / `中` / `高` / `极高`；未找到老人时为 `未知` |
| recommended_projects | array&lt;string&gt; | 推荐护理项目名称列表，依据风险等级从 `NursingProject` 中按类别挑选 |
| summary | string | 模板化生成的画像总结文本 |

`alert_stats[i]` 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| severity | string | 告警级别，取值 `low` / `medium` / `high` / `critical`（来自 `AlertSeverity`） |
| count | integer | 该级别告警条数 |

`recent_alerts[i]` 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| device_name | string | 告警设备名称 |
| severity | string | 告警级别（同上） |
| content | string | 告警内容 |
| created_at | string \| null | 告警创建时间（ISO 8601，UTC）；无时间时为 null |
| handled | boolean | 是否已处理，默认 false |

`top_devices[i]` 结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| device_name | string | 设备名称 |
| count | integer | 该设备告警次数 |

##### 响应示例

```json
{
  "elder_id": 3,
  "elder_name": "张桂兰",
  "health_summary": "高血压，轻度认知障碍，夜间跌倒史",
  "alert_total": 17,
  "alert_stats": [
    { "severity": "critical", "count": 1 },
    { "severity": "high", "count": 3 },
    { "severity": "medium", "count": 8 },
    { "severity": "low", "count": 5 }
  ],
  "recent_alerts": [
    {
      "device_name": "床垫传感器",
      "severity": "high",
      "content": "夜间离床超过 15 分钟",
      "created_at": "2026-07-15T22:41:00+00:00",
      "handled": false
    },
    {
      "device_name": "血压计",
      "severity": "medium",
      "content": "收缩压 165mmHg",
      "created_at": "2026-07-15T19:10:00+00:00",
      "handled": true
    }
  ],
  "top_devices": [
    { "device_name": "血压计", "count": 9 },
    { "device_name": "床垫传感器", "count": 5 },
    { "device_name": "紧急按钮", "count": 3 }
  ],
  "risk_score": 82,
  "risk_level": "极高",
  "recommended_projects": ["血压监测护理", "跌倒预防护理", "康复训练"],
  "summary": "老人 张桂兰 当前健康风险等级为「极高」（评分 82/100）。\n健康摘要：高血压，轻度认知障碍，夜间跌倒史\n累计告警 17 次，高频设备：血压计(9次)、床垫传感器(5次)、紧急按钮(3次)。\n建议重点关注护理项目：血压监测护理、跌倒预防护理、康复训练。"
}
```

未找到老人时的响应示例：

```json
{
  "elder_id": 999,
  "elder_name": "",
  "health_summary": "未找到该老人档案。",
  "alert_total": 0,
  "alert_stats": [],
  "recent_alerts": [],
  "top_devices": [],
  "risk_score": 0,
  "risk_level": "未知",
  "recommended_projects": [],
  "summary": "未找到该老人档案，无法生成画像。"
}
```

#### 错误码

| HTTP | 含义 | 触发场景 |
|------|------|----------|
| 422 | 参数校验失败 | `elder_id` 缺失或 ≤ 0 |
| 500 | 服务端错误 | 数据库查询异常（待补全局异常处理） |

#### 业务备注

- **风险评分规则**：`AlertSeverity` 权重为 `low=1` / `medium=5` / `high=12` / `critical=25`，按级别条数加权累加后封顶 100。
- **风险等级阈值**：≥80 `极高`；≥50 `高`；≥20 `中`；≥0 `低`。
- **推荐项目规则**：按风险等级映射偏好类别——`极高`：`medical/safety/rehab`；`高`：`safety/medical`；`中`：`safety/daily`；`低`：`daily`。每个类别从 `NursingProject` 中取首个匹配项，去重。
- 老人不存在时不抛 404，返回空画像 + `risk_level: "未知"`，前端可据此判断。
- 当前 `summary` 为模板生成，LLM 入口预留；接入真实模型后将由 `recommend` 节点的 `await llm.chat(...)` 增强。

---

## 7. 入住办理预览

- **方法**：`POST`
- **路径**：`/api/agent/admission/preview`
- **描述**：入住办理 Agent 的第一步。根据老人 ID 加载档案，挑选可用床位（可指定偏好床位），生成预览摘要并创建一条 `AdmissionRun` 记录，状态为 `WAITING_APPROVAL`，附带 15 分钟有效的 `reservation_token`，等待人工确认。
- **标签**：agent

#### 请求参数

##### Body（application/json）

| 字段 | 类型 | 必填 | 默认值 | 校验规则 | 说明 |
|------|------|------|--------|----------|------|
| elder_id | integer | 是 | - | > 0 | 老人 ID，对应 `Elder.id` |
| preferred_bed_id | integer \| null | 否 | null | > 0（非 null 时） | 偏好床位 ID；传入时若该床位可用则优先分配，否则回退到第一个可用床位 |

##### 请求示例

```json
{
  "elder_id": 3,
  "preferred_bed_id": 12
}
```

#### 响应

##### 200 成功（application/json）

| 字段 | 类型 | 说明 |
|------|------|------|
| run_id | integer | 入住办理运行记录 ID，对应 `AdmissionRun.id`；后续 confirm/cancel 必须携带 |
| status | string | 固定为 `WAITING_APPROVAL` |
| elder_name | string | 老人姓名 |
| bed_id | integer | 预分配床位 ID |
| bed_no | string | 预分配床位编号 |
| preview_summary | string | 预览摘要，包含老人姓名、床位、健康摘要、建议护理项目 |
| reservation_token | string | 预订令牌，URL 安全的随机串；confirm/cancel 时必须原样携带 |
| expires_at | string | 令牌过期时间（ISO 8601，UTC），距生成时刻 15 分钟 |

##### 响应示例

```json
{
  "run_id": 42,
  "status": "WAITING_APPROVAL",
  "elder_name": "张桂兰",
  "bed_id": 12,
  "bed_no": "A-101-2",
  "preview_summary": "老人 张桂兰 拟入住床位 A-101-2；健康摘要：高血压，轻度认知障碍，夜间跌倒史；建议护理项目：血压监测护理、跌倒预防护理、康复训练、紧急呼叫响应、用药提醒、日常巡视。",
  "reservation_token": "rZ4vPqL8m2kXyN6wA1bC9dE3fG",
  "expires_at": "2026-07-16T09:45:00+00:00"
}
```

#### 错误码

| HTTP | 含义 | 触发场景 |
|------|------|----------|
| 400 | 业务错误 | `ELDER_NOT_FOUND`：未找到老人 id=X |
| 400 | 业务错误 | `NO_AVAILABLE_BED`：当前没有可用床位 |
| 422 | 参数校验失败 | `elder_id` ≤ 0，或 `preferred_bed_id` ≤ 0 |
| 500 | 服务端错误 | 数据库写入异常（待补全局异常处理） |

错误响应体结构（HTTP 400）：

```json
{
  "detail": {
    "code": "ELDER_NOT_FOUND",
    "message": "未找到老人 id=999"
  }
}
```

#### 业务备注

- **15 分钟过期**：`reservation_token` 自生成起 15 分钟内有效（`RESERVATION_TTL_MINUTES = 15`）。超时后 confirm/cancel 会返回 `EXPIRED` 错误，并将 run 状态置为 `EXPIRED`，需重新调用 preview。
- **需人工确认**：preview 仅锁定信息与令牌，不修改床位状态；床位在 confirm 成功后才标记为 `occupied`。
- **床位选择逻辑**：若 `preferred_bed_id` 传入且该床位在可用列表中，则使用之；否则回退到可用列表第一个。`preferred_bed_id` 不存在或已占用不会报错，仅做回退。
- **预览摘要格式**：固定为 `老人 {name} 拟入住床位 {bed_no}；健康摘要：{health_summary}；建议护理项目：{projects}。`，建议项目取数据库前 6 个 `NursingProject.name` 拼接，无则显示"暂无"。
- 同一老人可多次调用 preview 生成多条 run，互不阻塞；请调用方自行管理活跃 run。

---

## 8. 入住办理确认

- **方法**：`POST`
- **路径**：`/api/agent/admission/confirm`
- **描述**：入住办理 Agent 的确认步骤。校验 `run_id` + `reservation_token`，将 run 状态置为 `COMPLETED`，并把预分配床位标记为 `occupied`。
- **标签**：agent

#### 请求参数

##### Body（application/json）

| 字段 | 类型 | 必填 | 默认值 | 校验规则 | 说明 |
|------|------|------|--------|----------|------|
| run_id | integer | 是 | - | > 0 | 入住办理运行记录 ID，由 preview 返回 |
| reservation_token | string | 是 | - | min_length=1 | 预订令牌，由 preview 返回；必须与 run 记录中存储的 token 完全一致 |

##### 请求示例

```json
{
  "run_id": 42,
  "reservation_token": "rZ4vPqL8m2kXyN6wA1bC9dE3fG"
}
```

#### 响应

##### 200 成功（application/json）

| 字段 | 类型 | 说明 |
|------|------|------|
| run_id | integer | 入住办理运行记录 ID |
| status | string | 固定为 `COMPLETED` |
| elder_id | integer | 老人 ID |
| bed_id | integer \| null | 入住房位 ID；正常情况下与 preview 一致，未分配床位时为 null |
| message | string | 固定为 `"入住已确认，床位已标记为已入住。"` |

##### 响应示例

```json
{
  "run_id": 42,
  "status": "COMPLETED",
  "elder_id": 3,
  "bed_id": 12,
  "message": "入住已确认，床位已标记为已入住。"
}
```

#### 错误码

| HTTP | 含义 | 触发场景 |
|------|------|----------|
| 400 | 业务错误 | `RUN_NOT_FOUND`：未找到入住办理记录 id=X |
| 400 | 业务错误 | `INVALID_STATUS`：run 当前状态非 `WAITING_APPROVAL`（如已确认/已取消/已过期） |
| 400 | 业务错误 | `TOKEN_INVALID`：`reservation_token` 为空或与记录不符 |
| 400 | 业务错误 | `STATE_INVALID`：预览状态异常，缺少过期时间（run 数据不完整） |
| 400 | 业务错误 | `EXPIRED`：token 已过期（超过 15 分钟），run 被置为 `EXPIRED`，需重新 preview |
| 422 | 参数校验失败 | `run_id` ≤ 0，或 `reservation_token` 为空字符串 |
| 500 | 服务端错误 | 数据库写入异常（待补全局异常处理） |

错误响应体结构（HTTP 400）：

```json
{
  "detail": {
    "code": "EXPIRED",
    "message": "预览已过期，请重新生成"
  }
}
```

#### 业务备注

- **床位状态副作用**：confirm 成功会把 `Bed.status` 从 `available` 置为 `occupied`；若床位在 preview 后被外部改动（如被其他 run 占用），当前实现仅在床位仍为 `available` 时才标记，否则保持现状（不会报错，待补充并发控制说明）。
- **token 一次性**：confirm 成功后 `AdmissionRun.reservation_token` 与 `expires_at` 被清空，无法再次确认。
- **过期处理**：token 过期时调用 confirm 不会确认成功，而是把 run 置为 `EXPIRED` 并返回 `EXPIRED` 错误，调用方需重新走 preview。
- **状态机**：仅 `WAITING_APPROVAL` 状态可被 confirm；其它状态一律返回 `INVALID_STATUS`。

---

## 9. 入住办理取消

- **方法**：`POST`
- **路径**：`/api/agent/admission/cancel`
- **描述**：入住办理 Agent 的取消步骤。校验 `run_id` + `reservation_token`，将 run 状态置为 `CANCELLED`。与 confirm 不同的是：**不修改床位状态**，仅作废预订令牌。
- **标签**：agent

#### 请求参数

##### Body（application/json）

| 字段 | 类型 | 必填 | 默认值 | 校验规则 | 说明 |
|------|------|------|--------|----------|------|
| run_id | integer | 是 | - | > 0 | 入住办理运行记录 ID，由 preview 返回 |
| reservation_token | string | 是 | - | min_length=1 | 预订令牌，由 preview 返回；必须与 run 记录中存储的 token 完全一致 |

##### 请求示例

```json
{
  "run_id": 42,
  "reservation_token": "rZ4vPqL8m2kXyN6wA1bC9dE3fG"
}
```

#### 响应

##### 200 成功（application/json）

| 字段 | 类型 | 说明 |
|------|------|------|
| run_id | integer | 入住办理运行记录 ID |
| status | string | 固定为 `CANCELLED` |
| elder_id | integer | 老人 ID |
| message | string | 固定为 `"入住预约已取消。"` |

##### 响应示例

```json
{
  "run_id": 42,
  "status": "CANCELLED",
  "elder_id": 3,
  "message": "入住预约已取消。"
}
```

#### 错误码

| HTTP | 含义 | 触发场景 |
|------|------|----------|
| 400 | 业务错误 | `RUN_NOT_FOUND`：未找到入住办理记录 id=X |
| 400 | 业务错误 | `INVALID_STATUS`：run 当前状态非 `WAITING_APPROVAL`（如已确认/已取消/已过期） |
| 400 | 业务错误 | `TOKEN_INVALID`：`reservation_token` 为空或与记录不符 |
| 400 | 业务错误 | `STATE_INVALID`：预览状态异常，缺少过期时间（run 数据不完整） |
| 400 | 业务错误 | `EXPIRED`：token 已过期（超过 15 分钟），run 被置为 `EXPIRED`，需重新 preview |
| 422 | 参数校验失败 | `run_id` ≤ 0，或 `reservation_token` 为空字符串 |
| 500 | 服务端错误 | 数据库写入异常（待补全局异常处理） |

错误响应体结构（HTTP 400）：

```json
{
  "detail": {
    "code": "TOKEN_INVALID",
    "message": "reservation token 无效"
  }
}
```

#### 业务备注

- **不释放床位**：cancel 不修改床位状态，因为 preview 阶段并未真正占用床位；床位始终是 `available`，直到 confirm 才变 `occupied`。
- **token 一次性**：cancel 成功后 `reservation_token` 与 `expires_at` 被清空，无法再次取消。
- **过期 run 不能取消**：若 token 已过期，cancel 同样返回 `EXPIRED` 并把 run 置为 `EXPIRED`（而非 `CANCELLED`）。
- **状态机**：仅 `WAITING_APPROVAL` 状态可被 cancel；其它状态一律返回 `INVALID_STATUS`。

---

## 附：admission 闭环调用流程

```
1. POST /api/agent/admission/preview
   → 返回 run_id + reservation_token + expires_at（15 分钟有效）
   → run 状态 = WAITING_APPROVAL

2a. POST /api/agent/admission/confirm  （人工确认）
    携带 run_id + reservation_token
    → run 状态 = COMPLETED，床位 = occupied
    → token 清空

2b. POST /api/agent/admission/cancel   （人工取消）
    携带 run_id + reservation_token
    → run 状态 = CANCELLED，床位不变
    → token 清空

3. 超时未处理（> 15 分钟）
   → 任何 confirm/cancel 调用都会把 run 置为 EXPIRED 并返回 EXPIRED 错误
   → 需重新走 preview
```

常见错误码对照：

| code | 含义 | 处理建议 |
|------|------|----------|
| `ELDER_NOT_FOUND` | 老人不存在 | 检查 `elder_id`，先调 `/api/nursing/elders` 查询 |
| `NO_AVAILABLE_BED` | 无可用床位 | 等待床位释放或新增床位 |
| `RUN_NOT_FOUND` | run 记录不存在 | 检查 `run_id`，必要时重新 preview |
| `INVALID_STATUS` | run 状态非 WAITING_APPROVAL | 已确认/取消/过期的 run 不能再操作，需重新 preview |
| `TOKEN_INVALID` | token 不匹配 | 核对 preview 返回的 `reservation_token`，避免拼写错误 |
| `STATE_INVALID` | run 数据不完整（缺过期时间） | 数据异常，需排查 `AdmissionRun` 记录 |
| `EXPIRED` | token 已过期 | 重新调用 preview 生成新 token |
