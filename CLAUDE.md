# CLAUDE.md — 代码主力指令

> 本文件是 Claude（代码主力）在本项目工作时的系统级指令。Claude Code 会自动读取。
> 你的职责：**编写与优化 zzyl_agent 后端代码、推进 agent 能力演进**。接口文档由 Codex 负责，你不要越界写文档，但你要保证代码里的 schema / 路由 / 注释足够清晰，让 Codex 能据此产出文档。

---

## 1. 项目概述

**zzyl_agent** 是一个智慧养老（ZZYL）场景的 agent 服务。后端用 FastAPI + LangGraph 编排多个养老业务 agent，前端是 React + Vite。

当前已落地的 4 个 agent 工作流：

| Agent | 入口文件 | 职责 |
|-------|---------|------|
| 通用对话 | `backend/app/agents/chat_graph.py` | 单轮问答 |
| 入住推荐 | `backend/app/agents/checkin_graph.py` | 根据老人档案 + 床位 + 护理项目给出入住建议 |
| 护理计划 | `backend/app/agents/care_plan_graph.py` | 生成护理计划草案 |
| 告警分析 | `backend/app/agents/alert_analysis_graph.py` | 分析设备告警并给处置建议 |

业务数据模型（`backend/app/models/nursing.py`）：Elder（老人）、Room（房间）、Bed（床位）、NursingProject（护理项目）、AlertRecord（告警记录）、CheckInApplication（入住申请）。

---

## 2. 技术栈与版本约束

- **Python >= 3.11**（用了 `StrEnum`、`X | None` 语法，不要降级写法）
- FastAPI >= 0.115 / Uvicorn / Pydantic-Settings
- LangGraph >= 0.2（agent 编排核心）/ LangChain >= 0.3（LLM 集成）
- SQLModel >= 0.0.22（ORM，同时是 Pydantic 模型）/ Alembic（迁移）
- 数据库：默认 SQLite（`sqlite:///./zzyl_agent.db`），生产可切 PostgreSQL
- 测试：pytest / ruff（line-length=100）/ mypy（strict）

**禁止**引入未在 `pyproject.toml` 声明的依赖；新增依赖必须先改 `pyproject.toml` 并单独提交一次。

---

## 3. 目录结构与职责

```
backend/app/
├── main.py              # FastAPI 入口，lifespan 建表，挂载路由
├── core/
│   ├── config.py        # Settings（env 驱动），lru_cache 单例
│   ├── database.py      # engine + get_session 依赖
│   └── llm.py           # LLMClient 协议 + provider 工厂
├── models/              # SQLModel 表模型（数据真相源）
├── schemas/             # Pydantic 请求/响应模型（API 边界）
├── agents/              # LangGraph 工作流（每个 agent 一个文件）
├── api/                 # 路由层，薄封装，只做参数校验与 graph 调度
└── prompts/             # 【待建】集中存放 prompt 模板
```

**分层铁律**：
- `models/` 是数据真相源，`schemas/` 是 API 边界，两者分离，不要让路由直接返回表模型之外的内部结构（现有 nursing 路由直接返回表模型可接受，但新接口优先用 schema）。
- `api/` 路由层必须薄：只做参数解析、依赖注入、调用 graph、返回响应。**业务逻辑写在 graph 节点或专门的 service 里**，不要堆在路由函数里。
- `agents/` 里每个 agent 一个文件，导出 `build_xxx_graph(...)` 工厂函数。

---

## 4. 代码规范

- **类型注解必填**：所有函数参数与返回值都要标注类型。mypy strict 已开启。
- **ruff line-length = 100**，超长就换行。
- 用现代 Python 语法：`X | None` 而非 `Optional[X]`，`list[T]` 而非 `List[T]`，`StrEnum` 而非 `Enum`。
- 异步优先：graph 节点、LLM 调用、路由 handler 都用 `async def`。
- 命名：类用 PascalCase，函数/变量用 snake_case，常量用 UPPER_SNAKE。
- 中文注释和 prompt 是允许的（业务面向中文用户），但变量名/函数名/类名一律英文。
- **不要留 TODO 不带上下文**：要么写明 `# TODO(模块): 描述 + 原因`，要么直接做掉。

---

## 5. Agent / Graph 开发约定（核心）

新增一个 agent 工作流时，严格按以下顺序：

1. **定义 State**：在 `agents/xxx_graph.py` 用 `TypedDict` 定义状态，字段要有默认占位（如 `answer: str`）。
2. **写节点函数**：节点是 `async def node(state) -> state`，纯函数风格，不直接持有外部资源；需要 session/llm 通过工厂闭包注入。
3. **写工厂**：`def build_xxx_graph(llm: LLMClient, session: Session | None = None)`，内部 `StateGraph` → `add_node` → `set_entry_point` → `add_edge(END)` → `compile()`。
4. **写 schema**：在 `schemas/agent.py` 加 `XxxRequest` / `XxxResponse`，字段加 `Field(...)` 校验。
5. **写路由**：在 `api/agent.py` 加 `@router.post(...)`，依赖注入 `llm` + `session`，调用 graph 后映射到响应模型。
6. **（可选）写测试**：`backend/tests/` 下加 pytest 用例，至少覆盖 happy path。

**prompt 管理**：现有 prompt 是硬编码在 graph 里的中文字符串。演进目标是把 prompt 抽到 `backend/app/prompts/` 目录（一个 agent 一个 `.py` 或 `.txt`），graph 里只组装变量后调用。新增 agent 时优先用集中模板。

**多节点编排**：现有 4 个 graph 都是单节点，没体现 LangGraph 的价值。重构时把复杂 agent 拆成多节点，例如告警分析可拆为：`采集数据 → 风险分级 → 处置建议`，用条件边做分级路由。

---

## 6. LLM 集成约定

现状：`core/llm.py` 只有 `MockLLMClient`，`llm_provider="mock"`。这是当前最大缺口。

**演进要求**：
- `LLMClient` 是协议（`Protocol`），所有 graph 只依赖这个协议，**禁止在 graph 里直接 import 具体厂商 SDK**。
- 在 `core/llm.py` 按 `settings.llm_provider` 工厂分发：`mock` / `openai` / `anthropic` / `deepseek` 等。
- 真实 provider 用 LangChain 的 `ChatOpenAI` / `ChatAnthropic` 适配，统一 `async def chat(prompt) -> str` 接口；流式场景扩展 `async def stream(prompt) -> AsyncIterator[str]`。
- API Key 等敏感配置走 `.env`，`Settings` 里加对应字段，**绝不硬编码密钥**，绝不把 `.env` 提交进 git（`.gitignore` 已忽略）。
- 新增 provider 时同步在 `.env.example` 补示例配置。

---

## 7. API 开发约定

- 全局前缀 `/api`（`settings.api_prefix`），agent 路由 `/api/agent/*`，nursing 路由 `/api/nursing/*`。
- 每个接口必须有：请求 schema（带 `Field` 校验）、响应 schema、路由 handler。
- 路径用复数名词 + kebab-case：`/agent/care-plan`、`/agent/alert-analysis`。
- 错误处理：graph 节点内部捕获异常并返回友好中文提示（如"未找到老人 X 的档案"），不要把异常栈抛到客户端。后续补全局异常中间件统一 422/500。
- 流式接口约定（待建）：`POST /agent/chat/stream` 用 SSE，`text/event-stream`，事件格式 `data: {"token": "..."}`。

---

## 8. Git 提交规范（重点）

**核心原则：少量多次，接口完成即提交。**

- 每完成一个**独立可验证的小单元**就提交一次，不要攒一大堆改动一次提交。典型粒度：
  - 新增/修改一个 schema → 可单独提交
  - 新增一个 graph 节点或 agent → 单独提交
  - **一个接口开发完成（schema + 路由 + graph + 必要测试）→ 必须立即提交**，不要等一批接口一起
  - 修一个 bug → 单独提交
  - 改配置/依赖 → 单独提交
- **提交信息格式**（Conventional Commits）：
  ```
  type(scope): 简短中文描述

  type ∈ feat | fix | refactor | docs | test | chore | perf
  scope ∈ agent | nursing | llm | db | api | config | prompt | test | docs
  ```
  示例：
  - `feat(agent): 新增护理计划流式接口`
  - `fix(llm): 修复 OpenAI provider 流式中断问题`
  - `refactor(api): 路由层抽离 session 依赖`
  - `chore(config): 升级 langgraph 至 0.2.x`
- **一个提交只做一件事**。如果改了 LLM 又改了路由，拆成两个提交。
- 提交前确保 `ruff check .` 与 `mypy .` 通过（有测试则 `pytest` 通过）。
- 不要 `--no-verify` 跳过钩子。
- 接口相关提交后，**主动通知 Codex 同步更新对应接口文档**（在协作说明里约定）。

---

## 9. 优化演进路线（按优先级推进）

这是项目的演进方向，按阶段推进，每个阶段完成后提交：

### 阶段 1 — 接真实 LLM（最高优先）
- `core/llm.py` 实现 `OpenAILLMClient` / `AnthropicLLMClient`，走 LangChain 适配
- `Settings` 增加 `llm_api_key` / `llm_model` / `llm_base_url` 等字段
- prompt 抽到 `app/prompts/` 集中管理
- 补 `.env.example`

### 阶段 2 — 流式输出
- `LLMClient` 增加 `stream` 方法
- `POST /api/agent/chat/stream` SSE 接口
- LangGraph 用 `astream_events` 做节点级流式

### 阶段 3 — 会话记忆
- 新增 `ConversationRecord` / `MessageRecord` 表模型
- `chat_graph` 读取历史对话作为上下文
- `conversation_id` 真正生效（生成、持久化、回查）

### 阶段 4 — 多节点编排 + 工具调用
- 告警分析拆多节点 + 条件边分级
- agent 支持工具调用（查床位、查老人档案、查护理项目），用 LangGraph 的 ToolNode
- 让 agent 能自主决定调用哪些查询工具

### 阶段 5 — 可观测性与质量
- 结构化日志（structlog 或 loguru）
- 全局异常中间件 + 统一错误响应
- pytest 覆盖核心 graph 与路由
- Alembic 迁移脚本（替代 `create_all`）

### 新功能候选（按需排期）
- 每日护理交班报告自动生成
- 老人健康趋势分析（基于告警历史聚合）
- 床位智能匹配（入住推荐升级，多约束求解）
- 家属端问答 agent（受限于本人老人的信息）
- 护理计划执行回写与完成度统计

---

## 10. 与 Codex 的协作约定

- **分工**：你写代码，Codex 写接口文档。你**不要**自己写 `docs/api/` 下的接口文档。
- **你的义务**：保证 `schemas/` 与路由签名为文档提供准确依据；接口字段变动时，在提交信息里写清 `scope: api` 并在协作说明里提示 Codex 同步。
- **文档规范**见 `docs/api/README.md` 与 `CODEX.md`，你开发新接口时按这个规范留好字段说明，便于 Codex 转写。
- 当 Codex 反馈某接口字段缺说明时，优先补代码里的 docstring / `Field(description=...)`，而不是直接改文档。

---

## 11. 常用命令

```bash
# 安装依赖（在 backend/ 下）
pip install -e ".[dev]"

# 启动开发服务（热重载）
uvicorn app.main:app --reload --app-dir backend

# 种子数据
curl -X POST http://localhost:8000/api/nursing/demo/seed

# lint / 类型检查
ruff check .
mypy .

# 测试
pytest
```
