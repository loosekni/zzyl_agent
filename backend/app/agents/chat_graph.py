from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.core.llm import LLMClient
from app.prompts.agent import build_chat_prompt


class ChatState(TypedDict):
    message: str
    history: str
    answer: str


def build_chat_graph(llm: LLMClient) -> CompiledStateGraph[ChatState, None, Any, ChatState]:
    async def respond(state: ChatState) -> ChatState:
        prompt = build_chat_prompt(state["message"], state.get("history", ""))
        answer = await llm.chat(prompt)
        return {"message": state["message"], "history": state.get("history", ""), "answer": answer}

    graph = StateGraph(ChatState)
    graph.add_node("respond", respond)
    graph.set_entry_point("respond")
    graph.add_edge("respond", END)
    return graph.compile()
