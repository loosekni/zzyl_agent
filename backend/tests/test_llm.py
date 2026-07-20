import pytest

from app.core.config import Settings
from app.core.llm import LangChainLLMClient, MockLLMClient, build_llm_client


@pytest.mark.anyio
async def test_mock_llm_stream_matches_chat_response() -> None:
    client = MockLLMClient()

    chunks = [chunk async for chunk in client.stream("测试流式")]

    assert "".join(chunks) == await client.chat("测试流式")
    assert chunks


def test_build_llm_client_defaults_to_mock() -> None:
    client = build_llm_client(Settings())

    assert isinstance(client, MockLLMClient)


def test_build_llm_client_rejects_unknown_provider() -> None:
    settings = Settings(llm_provider="unknown")

    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        build_llm_client(settings)


def test_real_provider_requires_api_key() -> None:
    settings = Settings(llm_provider="anthropic", llm_model="claude-opus-4-8")

    with pytest.raises(ValueError, match="requires llm_api_key"):
        build_llm_client(settings)


def test_build_openai_compatible_provider() -> None:
    settings = Settings(
        llm_provider="deepseek",
        llm_api_key="test-key",
        llm_model="deepseek-chat",
        llm_base_url="https://api.deepseek.com",
    )

    client = build_llm_client(settings)

    assert isinstance(client, LangChainLLMClient)


def test_build_anthropic_provider() -> None:
    settings = Settings(
        llm_provider="anthropic",
        llm_api_key="test-key",
        llm_model="claude-opus-4-8",
    )

    client = build_llm_client(settings)

    assert isinstance(client, LangChainLLMClient)
