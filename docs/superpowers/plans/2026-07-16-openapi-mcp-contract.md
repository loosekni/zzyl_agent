# OpenAPI + MCP Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate synchronized OpenAPI/Markdown contracts and expose the FastAPI capabilities through a local stdio MCP server for Claude Code.

**Architecture:** FastAPI remains the source of truth. A thin MCP adapter invokes the existing HTTP application through an injectable ASGI client, while a documentation script serializes `app.openapi()` and a curated MCP tool manifest. No MCP tool accesses the database directly.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, MCP Python SDK, pytest, httpx.

---

### Task 1: MCP tool manifest and invocation contract

**Files:**
- Create: `backend/app/mcp/manifest.py`
- Create: `backend/app/mcp/server.py`
- Test: `backend/tests/test_mcp_contract.py`

- [ ] Write tests for stable tool names, descriptions, argument schemas, HTTP method/path mapping, and rejection of unknown tools.
- [ ] Run `pytest backend/tests/test_mcp_contract.py -q` and confirm it fails because the MCP package does not exist.
- [ ] Implement a typed manifest and MCP server factory using the MCP Python SDK; dispatch through an injected async HTTP caller.
- [ ] Run the focused tests and confirm they pass.

### Task 2: OpenAPI and Markdown generation

**Files:**
- Create: `backend/scripts/generate_api_docs.py`
- Create: `backend/tests/test_api_docs.py`
- Create: `docs/api.md`
- Create: `docs/mcp-tools.md`
- Create: `docs/openapi.json`

- [ ] Write tests that generate docs into a temporary directory and assert OpenAPI paths and every MCP manifest tool are present.
- [ ] Run the focused tests and confirm failure before implementation.
- [ ] Implement deterministic JSON/Markdown generation with a `--check` mode that exits non-zero on drift.
- [ ] Run focused tests and regenerate checked-in docs.

### Task 3: Configuration and Claude launch entrypoint

**Files:**
- Modify: `backend/pyproject.toml`
- Create: `backend/app/mcp/__init__.py`
- Create: `claude.mcp.json`
- Test: `backend/tests/test_mcp_config.py`

- [ ] Add `mcp` and test dependencies, then test the config points at the stdio module.
- [ ] Add a module entrypoint that runs the MCP server over stdio without starting a second web server.
- [ ] Verify config parsing and module import.

### Task 4: Verification and handoff

**Files:**
- Modify: `task_plan.md`
- Modify: `progress.md`

- [ ] Run the full Python test suite and the documentation `--check` command.
- [ ] Inspect git diff and record remaining limitations, especially that this is Claude -> ZZYL communication only.
