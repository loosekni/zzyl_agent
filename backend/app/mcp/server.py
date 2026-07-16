import json
import os
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from app.mcp.manifest import MCP_TOOLS


def _base_url() -> str:
    return os.getenv("ZZYL_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


async def _call(method: str, path: str, arguments: dict[str, Any]) -> str:
    async with httpx.AsyncClient(base_url=_base_url(), timeout=30.0) as client:
        response = await client.request(method, path, json=arguments if method != "GET" else None)
        response.raise_for_status()
        payload: Any = response.json()
    return json.dumps(payload, ensure_ascii=False)


def create_mcp_server() -> FastMCP:
    server = FastMCP(
        "ZZYL Agent",
        instructions="Use governed ZZYL APIs. Do not infer permissions or bypass human admission confirmation.",
    )

    @server.tool(name="agent.chat", description=MCP_TOOLS[0].description)
    async def agent_chat(message: str, conversation_id: str | None = None) -> str:
        return await _call("POST", "/api/agent/chat", {"message": message, "conversation_id": conversation_id})

    @server.tool(name="agent.checkin_recommendation", description=MCP_TOOLS[1].description)
    async def agent_checkin_recommendation(elder_name: str) -> str:
        return await _call("POST", "/api/agent/checkin/recommendation", {"elder_name": elder_name})

    @server.tool(name="agent.care_plan", description=MCP_TOOLS[2].description)
    async def agent_care_plan(elder_name: str, care_goal: str = "") -> str:
        return await _call("POST", "/api/agent/care-plan", {"elder_name": elder_name, "care_goal": care_goal})

    @server.tool(name="agent.alert_analysis", description=MCP_TOOLS[3].description)
    async def agent_alert_analysis(alert_id: int) -> str:
        return await _call("POST", "/api/agent/alert-analysis", {"alert_id": alert_id})

    @server.tool(name="nursing.list_elders", description=MCP_TOOLS[4].description)
    async def nursing_list_elders() -> str:
        return await _call("GET", "/api/nursing/elders", {})

    @server.tool(name="nursing.list_rooms", description=MCP_TOOLS[5].description)
    async def nursing_list_rooms() -> str:
        return await _call("GET", "/api/nursing/rooms", {})

    @server.tool(name="nursing.list_beds", description=MCP_TOOLS[6].description)
    async def nursing_list_beds() -> str:
        return await _call("GET", "/api/nursing/beds", {})

    @server.tool(name="nursing.list_projects", description=MCP_TOOLS[7].description)
    async def nursing_list_projects() -> str:
        return await _call("GET", "/api/nursing/projects", {})

    @server.tool(name="nursing.list_alerts", description=MCP_TOOLS[8].description)
    async def nursing_list_alerts() -> str:
        return await _call("GET", "/api/nursing/alerts", {})

    @server.tool(name="nursing.list_checkins", description=MCP_TOOLS[9].description)
    async def nursing_list_checkins() -> str:
        return await _call("GET", "/api/nursing/checkins", {})

    @server.tool(name="nursing.seed_demo_data", description=MCP_TOOLS[10].description)
    async def nursing_seed_demo_data() -> str:
        return await _call("POST", "/api/nursing/demo/seed", {})

    return server


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] != "--stdio":
        raise SystemExit(f"Unsupported MCP transport: {sys.argv[1]}")
    create_mcp_server().run(transport="stdio")


if __name__ == "__main__":
    main()
