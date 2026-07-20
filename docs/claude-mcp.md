# Claude MCP 接入

## 启动前提

先启动 FastAPI：

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Claude Code 使用仓库根目录的 `claude.mcp.json` 启动本地 stdio MCP 服务。服务通过 `ZZYL_API_BASE_URL` 调用 FastAPI，不直接访问数据库。

## 文档同步

从仓库根目录执行：

```powershell
cd backend
py -3.14 -m scripts.generate_api_docs
py -3.14 -m scripts.generate_api_docs --check
```

接口或 MCP 工具清单变更后，必须重新生成 `docs/openapi.json`、`docs/api.md` 和 `docs/mcp-tools.md`；`--check` 返回非零表示存在文档漂移。

## 安全边界

MCP 工具只代理现有 FastAPI 接口。当前项目没有暴露 admission 写入工具；后续增加 `preview/confirm/cancel` 时，必须保留基线项目要求的人工确认、run 绑定和 token 校验。
