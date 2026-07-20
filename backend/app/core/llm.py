from collections.abc import AsyncIterator
from typing import Protocol


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


def get_llm_client() -> LLMClient:
    return MockLLMClient()
