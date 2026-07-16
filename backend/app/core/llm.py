from typing import Protocol


class LLMClient(Protocol):
    async def chat(self, prompt: str) -> str:
        pass


class MockLLMClient:
    async def chat(self, prompt: str) -> str:
        return f"已收到请求：{prompt}"


def get_llm_client() -> LLMClient:
    return MockLLMClient()
