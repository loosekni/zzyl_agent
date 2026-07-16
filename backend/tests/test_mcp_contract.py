import pytest

from app.mcp.manifest import MCP_TOOLS, get_tool


def test_manifest_contains_existing_agent_and_nursing_capabilities() -> None:
    names = {tool.name for tool in MCP_TOOLS}

    assert {
        "agent.chat",
        "agent.checkin_recommendation",
        "agent.care_plan",
        "agent.alert_analysis",
        "nursing.list_elders",
        "nursing.list_alerts",
        "nursing.seed_demo_data",
    } <= names


def test_tool_contract_has_http_mapping_and_json_schema() -> None:
    tool = get_tool("agent.chat")

    assert tool.method == "POST"
    assert tool.path == "/api/agent/chat"
    assert tool.input_schema["type"] == "object"
    assert "message" in tool.input_schema["required"]


def test_unknown_tool_is_rejected() -> None:
    with pytest.raises(KeyError, match="Unknown MCP tool"):
        get_tool("agent.does_not_exist")
