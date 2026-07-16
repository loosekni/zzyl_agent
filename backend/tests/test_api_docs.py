import json

from scripts.generate_api_docs import generate_docs


class FakeApp:
    def openapi(self) -> dict:
        return {"openapi": "3.1.0", "paths": {"/api/health": {"get": {"summary": "Health"}}}}


def test_generate_docs_writes_openapi_and_mcp_manifest(tmp_path) -> None:
    generate_docs(FakeApp(), tmp_path)

    openapi = json.loads((tmp_path / "openapi.json").read_text(encoding="utf-8"))
    api_doc = (tmp_path / "api.md").read_text(encoding="utf-8")
    mcp_doc = (tmp_path / "mcp-tools.md").read_text(encoding="utf-8")

    assert openapi["paths"]["/api/health"]["get"]["summary"] == "Health"
    assert "GET /api/health" in api_doc
    assert "agent.chat" in mcp_doc
    assert "nursing.seed_demo_data" in mcp_doc


def test_check_mode_detects_document_drift(tmp_path) -> None:
    generate_docs(FakeApp(), tmp_path)
    (tmp_path / "api.md").write_text("stale", encoding="utf-8")

    assert generate_docs(FakeApp(), tmp_path, check=True) is False
