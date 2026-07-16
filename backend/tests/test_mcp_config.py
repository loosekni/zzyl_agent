import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_claude_config_starts_stdio_server() -> None:
    config = json.loads((ROOT / "claude.mcp.json").read_text(encoding="utf-8"))
    server = config["mcpServers"]["zzyl-agent"]

    assert server["command"] == "python"
    assert server["args"][-3:] == ["-m", "app.mcp.server", "--stdio"]

