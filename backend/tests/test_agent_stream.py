import json

from fastapi.testclient import TestClient

from app.main import app


def test_chat_stream_emits_sse_tokens_and_done() -> None:
    with TestClient(app) as client:
        response = client.post("/api/agent/chat/stream", json={"message": "你好"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = [line.removeprefix("data: ") for line in response.text.splitlines() if line]
    assert events[-1] == "[DONE]"

    token_payloads = [json.loads(event) for event in events[:-1]]
    assert "".join(payload["token"] for payload in token_payloads) == "已收到请求：你好"
