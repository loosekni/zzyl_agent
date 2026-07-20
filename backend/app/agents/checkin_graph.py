from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from sqlmodel import Session, select

from app.core.llm import LLMClient
from app.models.nursing import Bed, BedStatus, Elder, NursingProject
from app.prompts.agent import build_checkin_recommendation_prompt


class RecommendationState(TypedDict):
    elder_name: str
    suggestion: str


async def _build_suggestion(session: Session, elder_name: str, llm: LLMClient) -> str:
    elder = session.exec(select(Elder).where(Elder.name == elder_name)).first()
    available_beds = list(session.exec(select(Bed).where(Bed.status == BedStatus.available)).all())
    projects = list(session.exec(select(NursingProject)).all())

    if elder is None:
        return f"未找到老人 {elder_name} 的档案。"

    prompt = build_checkin_recommendation_prompt(
        elder_name=elder.name,
        health_summary=elder.health_summary,
        available_bed_count=len(available_beds),
        nursing_project_count=len(projects),
    )
    return await llm.chat(prompt)


def build_checkin_recommendation_graph(
    llm: LLMClient, session: Session
) -> CompiledStateGraph[RecommendationState, None, Any, RecommendationState]:
    async def recommend(state: RecommendationState) -> RecommendationState:
        suggestion = await _build_suggestion(session, state["elder_name"], llm)
        return {"elder_name": state["elder_name"], "suggestion": suggestion}

    graph = StateGraph(RecommendationState)
    graph.add_node("recommend", recommend)
    graph.set_entry_point("recommend")
    graph.add_edge("recommend", END)
    return graph.compile()
