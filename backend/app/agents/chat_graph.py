from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.core.llm import LLMClient


class ChatState(TypedDict):
    message: str
    answer: str


def build_chat_graph(llm: LLMClient) -> CompiledStateGraph[ChatState, None, Any, ChatState]:
    async def respond(state: ChatState) -> ChatState:
        answer = await llm.chat(state["message"])
        return {"message": state["message"], "answer": answer}

    graph = StateGraph(ChatState)
    graph.add_node("respond", respond)
    graph.set_entry_point("respond")
    graph.add_edge("respond", END)
    return graph.compile()
