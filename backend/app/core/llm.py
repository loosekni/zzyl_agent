from collections.abc import AsyncIterator
from typing import Any, Protocol

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage
from langchain_openai import ChatOpenAI

from app.core.config import Settings, get_settings


class LLMClient(Protocol):
    async def chat(self, prompt: str) -> str:
        pass

    def stream(self, prompt: str) -> AsyncIterator[str]:
        pass


class MockLLMClient:
    async def chat(self, prompt: str) -> str:
        return f"已收到请求：{prompt}"

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        response = await self.chat(prompt)
        for character in response:
            yield character


class LangChainLLMClient:
    def __init__(self, model: BaseChatModel):
        self.model = model

    async def chat(self, prompt: str) -> str:
        message = await self.model.ainvoke(prompt)
        return _message_content_to_text(message)

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        async for chunk in self.model.astream(prompt):
            text = _message_content_to_text(chunk)
            if text:
                yield text


def get_llm_client() -> LLMClient:
    return build_llm_client(get_settings())


def build_llm_client(settings: Settings) -> LLMClient:
    provider = settings.llm_provider.strip().lower()
    if provider == "mock":
        return MockLLMClient()
    if provider in {"openai", "deepseek"}:
        return LangChainLLMClient(_build_openai_compatible_model(settings))
    if provider == "anthropic":
        return LangChainLLMClient(_build_anthropic_model(settings))
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def _build_openai_compatible_model(settings: Settings) -> ChatOpenAI:
    _require_api_key(settings)
    kwargs: dict[str, Any] = {
        "api_key": settings.llm_api_key,
        "model": settings.llm_model,
        "temperature": settings.llm_temperature,
    }
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    return ChatOpenAI(**kwargs)


def _build_anthropic_model(settings: Settings) -> ChatAnthropic:
    _require_api_key(settings)
    kwargs: dict[str, Any] = {
        "api_key": settings.llm_api_key,
        "model_name": settings.llm_model,
        "temperature": settings.llm_temperature,
    }
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    return ChatAnthropic(**kwargs)


def _require_api_key(settings: Settings) -> None:
    if not settings.llm_api_key:
        raise ValueError(f"LLM provider {settings.llm_provider} requires llm_api_key")


def _message_content_to_text(message: BaseMessage | AIMessageChunk) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            text = item.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "".join(parts)
