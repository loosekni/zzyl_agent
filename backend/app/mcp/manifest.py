from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MCPTool:
    name: str
    description: str
    method: str
    path: str
    input_schema: dict[str, Any]


_NO_ARGS: dict[str, Any] = {"type": "object", "properties": {}, "additionalProperties": False}

MCP_TOOLS: tuple[MCPTool, ...] = (
    MCPTool(
        "agent.chat",
        "Send a natural-language request to the ZZYL agent.",
        "POST",
        "/api/agent/chat",
        {"type": "object", "properties": {"message": {"type": "string", "minLength": 1}, "conversation_id": {"type": ["string", "null"]}}, "required": ["message"], "additionalProperties": False},
    ),
    MCPTool(
        "agent.checkin_recommendation",
        "Generate a check-in recommendation for an elder.",
        "POST",
        "/api/agent/checkin/recommendation",
        {"type": "object", "properties": {"elder_name": {"type": "string", "minLength": 1}}, "required": ["elder_name"], "additionalProperties": False},
    ),
    MCPTool(
        "agent.care_plan",
        "Generate a care plan draft for an elder and goal.",
        "POST",
        "/api/agent/care-plan",
        {"type": "object", "properties": {"elder_name": {"type": "string", "minLength": 1}, "care_goal": {"type": "string"}}, "required": ["elder_name"], "additionalProperties": False},
    ),
    MCPTool(
        "agent.alert_analysis",
        "Analyze a persisted alert by id.",
        "POST",
        "/api/agent/alert-analysis",
        {"type": "object", "properties": {"alert_id": {"type": "integer", "exclusiveMinimum": 0}}, "required": ["alert_id"], "additionalProperties": False},
    ),
    MCPTool("nursing.list_elders", "List elders visible to the service.", "GET", "/api/nursing/elders", _NO_ARGS),
    MCPTool("nursing.list_rooms", "List rooms visible to the service.", "GET", "/api/nursing/rooms", _NO_ARGS),
    MCPTool("nursing.list_beds", "List beds visible to the service.", "GET", "/api/nursing/beds", _NO_ARGS),
    MCPTool("nursing.list_projects", "List nursing projects.", "GET", "/api/nursing/projects", _NO_ARGS),
    MCPTool("nursing.list_alerts", "List alert records.", "GET", "/api/nursing/alerts", _NO_ARGS),
    MCPTool("nursing.list_checkins", "List check-in applications.", "GET", "/api/nursing/checkins", _NO_ARGS),
    MCPTool("nursing.seed_demo_data", "Seed idempotent local demonstration data.", "POST", "/api/nursing/demo/seed", _NO_ARGS),
)


def get_tool(name: str) -> MCPTool:
    for tool in MCP_TOOLS:
        if tool.name == name:
            return tool
    raise KeyError(f"Unknown MCP tool: {name}")

