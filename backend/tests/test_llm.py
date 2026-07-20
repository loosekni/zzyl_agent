import pytest

from app.core.llm import MockLLMClient


@pytest.mark.anyio
async def test_mock_llm_stream_matches_chat_response() -> None:
    client = MockLLMClient()

    chunks = [chunk async for chunk in client.stream("测试流式")]

    assert "".join(chunks) == await client.chat("测试流式")
    assert chunks
