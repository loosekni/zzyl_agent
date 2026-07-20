import json
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.database import get_session
from app.main import app
from app.models.nursing import ConversationRecord, MessageRecord, MessageRole


@contextmanager
def _client_with_temp_db(tmp_path: Path) -> Generator[TestClient, None, None]:
    engine = create_engine(f"sqlite:///{tmp_path / 'chat.db'}")
    SQLModel.metadata.create_all(engine)

    def override_get_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


def _events(response_text: str) -> list[str]:
    return [line.removeprefix("data: ") for line in response_text.splitlines() if line]


def test_chat_creates_conversation_and_persists_messages(tmp_path: Path) -> None:
    with _client_with_temp_db(tmp_path) as client:
        response = client.post("/api/agent/chat", json={"message": "第一句"})
        assert response.status_code == 200
        payload = response.json()
        conversation_id = payload["conversation_id"]

        followup = client.post(
            "/api/agent/chat",
            json={"message": "第二句", "conversation_id": conversation_id},
        )
        assert followup.status_code == 200
        assert followup.json()["conversation_id"] == conversation_id

        with Session(create_engine(f"sqlite:///{tmp_path / 'chat.db'}")) as session:
            conversation = session.get(ConversationRecord, conversation_id)
            messages = list(
                session.exec(
                    select(MessageRecord).where(MessageRecord.conversation_id == conversation_id)
                ).all()
            )

    assert conversation is not None
    assert [message.role for message in messages] == [
        MessageRole.user,
        MessageRole.assistant,
        MessageRole.user,
        MessageRole.assistant,
    ]
    assert messages[0].content == "第一句"
    assert "以下是当前会话的历史消息" in messages[3].content


def test_chat_stream_emits_conversation_id_and_persists_messages(tmp_path: Path) -> None:
    with _client_with_temp_db(tmp_path) as client:
        response = client.post("/api/agent/chat/stream", json={"message": "stream memory"})

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        events = _events(response.text)
        conversation_id = json.loads(events[0])["conversation_id"]
        token_payloads = [json.loads(event) for event in events[1:-1]]

        with Session(create_engine(f"sqlite:///{tmp_path / 'chat.db'}")) as session:
            messages = list(
                session.exec(
                    select(MessageRecord).where(MessageRecord.conversation_id == conversation_id)
                ).all()
            )

    assert events[-1] == "[DONE]"
    assert "".join(payload["token"] for payload in token_payloads) == "已收到请求：stream memory"
    assert [message.role for message in messages] == [MessageRole.user, MessageRole.assistant]
