"""Generate checked-in OpenAPI and Claude-facing MCP documentation."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from app.mcp.manifest import MCP_TOOLS


def _render_api_markdown(schema: dict[str, Any]) -> str:
    lines = ["# ZZYL HTTP API", "", "Generated from the FastAPI application.", ""]
    for path, operations in sorted(schema.get("paths", {}).items()):
        for method, operation in sorted(operations.items()):
            if method.startswith("x-"):
                continue
            summary = operation.get("summary") or operation.get("operationId") or ""
            lines.append(f"## {method.upper()} {path}")
            if summary:
                lines.append(f"{summary}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_mcp_markdown() -> str:
    lines = [
        "# ZZYL MCP Tools",
        "",
        "This manifest is generated from `backend/app/mcp/manifest.py`.",
        "Claude must use the governed HTTP mapping and must not bypass admission confirmation.",
        "",
    ]
    for tool in MCP_TOOLS:
        lines.extend([f"## `{tool.name}`", "", tool.description, "", f"- HTTP: `{tool.method} {tool.path}`", f"- Input schema: `{json.dumps(tool.input_schema, ensure_ascii=False, sort_keys=True)}`", ""])
    return "\n".join(lines).rstrip() + "\n"


def _write_or_check(path: Path, content: str, check: bool) -> bool:
    if check:
        return path.exists() and path.read_text(encoding="utf-8") == content
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def generate_docs(app: Any, output_dir: Path, check: bool = False) -> bool:
    schema = app.openapi()
    outputs = {
        output_dir / "openapi.json": json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        output_dir / "api.md": _render_api_markdown(schema),
        output_dir / "mcp-tools.md": _render_mcp_markdown(),
    }
    results = [_write_or_check(path, content, check) for path, content in outputs.items()]
    return all(results)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "docs")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    from app.main import app

    if args.check:
        with tempfile.TemporaryDirectory() as directory:
            expected_dir = Path(directory)
            generate_docs(app, expected_dir)
            mismatches = []
            for name in ("openapi.json", "api.md", "mcp-tools.md"):
                expected = (expected_dir / name).read_text(encoding="utf-8")
                actual_path = args.output_dir / name
                if not actual_path.exists() or actual_path.read_text(encoding="utf-8") != expected:
                    mismatches.append(name)
            if mismatches:
                print(f"Documentation drift: {', '.join(mismatches)}")
                return 1
            return 0

    generate_docs(app, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

