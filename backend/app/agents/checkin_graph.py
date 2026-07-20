import json
from typing import Any, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from sqlmodel import Session

from app.core.llm import LLMClient
from app.prompts.agent import build_checkin_recommendation_prompt
from app.tools.nursing import build_checkin_context_tools


class RecommendationState(TypedDict):
    elder_name: str
    messages: list[AnyMessage]
    suggestion: str


def _prepare_tool_calls(state: RecommendationState) -> RecommendationState:
    tool_calls = [
        {
            "name": "get_elder_profile",
            "args": {"elder_name": state["elder_name"]},
            "id": "elder-profile",
            "type": "tool_call",
        },
        {
            "name": "get_bed_availability",
            "args": {},
            "id": "bed-availability",
            "type": "tool_call",
        },
        {
            "name": "get_nursing_project_catalog",
            "args": {},
            "id": "nursing-project-catalog",
            "type": "tool_call",
        },
    ]
    message = AIMessage(content="", tool_calls=tool_calls)
    return {**state, "messages": [message]}


async def _build_suggestion(state: RecommendationState, llm: LLMClient) -> RecommendationState:
    tool_results = _parse_tool_results(state["messages"])
    elder_profile = tool_results.get("get_elder_profile", {})
    if not elder_profile.get("found"):
        return {**state, "suggestion": f"未找到老人 {state['elder_name']} 的档案。"}

    bed_availability = tool_results.get("get_bed_availability", {})
    project_catalog = tool_results.get("get_nursing_project_catalog", {})
    prompt = build_checkin_recommendation_prompt(
        elder_name=str(elder_profile.get("name", state["elder_name"])),
        health_summary=str(elder_profile.get("health_summary", "无")),
        available_bed_count=int(bed_availability.get("available_bed_count", 0)),
        nursing_project_count=int(project_catalog.get("nursing_project_count", 0)),
    )
    return {**state, "suggestion": await llm.chat(prompt)}


def _parse_tool_results(messages: list[AnyMessage]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for message in messages:
        if isinstance(message, ToolMessage):
            payload = json.loads(str(message.content))
            if isinstance(payload, dict):
                results[message.name or ""] = payload
    return results


def build_checkin_recommendation_graph(
    llm: LLMClient, session: Session
) -> CompiledStateGraph[RecommendationState, None, Any, RecommendationState]:
    async def recommend(state: RecommendationState) -> RecommendationState:
        return await _build_suggestion(state, llm)

    graph = StateGraph(RecommendationState)
    graph.add_node("prepare_tools", _prepare_tool_calls)
    graph.add_node("tools", ToolNode(build_checkin_context_tools(session)))
    graph.add_node("recommend", recommend)
    graph.set_entry_point("prepare_tools")
    graph.add_edge("prepare_tools", "tools")
    graph.add_edge("tools", "recommend")
    graph.add_edge("recommend", END)
    return graph.compile()
