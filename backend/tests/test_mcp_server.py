from app.mcp.manifest import MCP_TOOLS
from app.mcp.server import create_mcp_server


def test_server_registers_every_manifest_tool() -> None:
    server = create_mcp_server()

    assert set(server._tool_manager._tools) == {tool.name for tool in MCP_TOOLS}
