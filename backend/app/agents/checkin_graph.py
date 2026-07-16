from typing import TypedDict

from langgraph.graph import END, StateGraph
from sqlmodel import Session, select

from app.core.llm import LLMClient
from app.models.nursing import Bed, BedStatus, Elder, NursingProject


class RecommendationState(TypedDict):
    elder_name: str
    suggestion: str


async def _build_suggestion(session: Session, elder_name: str, llm: LLMClient) -> str:
    elder = session.exec(select(Elder).where(Elder.name == elder_name)).first()
    available_beds = list(session.exec(select(Bed).where(Bed.status == BedStatus.available)).all())
    projects = list(session.exec(select(NursingProject)).all())

    if elder is None:
        return f"未找到老人 {elder_name} 的档案。"

    prompt = (
        f"老人姓名：{elder.name}\n"
        f"健康摘要：{elder.health_summary or '无'}\n"
        f"可用床位数：{len(available_beds)}\n"
        f"护理项目数：{len(projects)}\n"
        "请给出简短入住建议，包含床位匹配、护理关注点和下一步动作。"
    )
    return await llm.chat(prompt)


def build_checkin_recommendation_graph(llm: LLMClient, session: Session):
    async def recommend(state: RecommendationState) -> RecommendationState:
        suggestion = await _build_suggestion(session, state["elder_name"], llm)
        return {"elder_name": state["elder_name"], "suggestion": suggestion}

    graph = StateGraph(RecommendationState)
    graph.add_node("recommend", recommend)
    graph.set_entry_point("recommend")
    graph.add_edge("recommend", END)
    return graph.compile()
