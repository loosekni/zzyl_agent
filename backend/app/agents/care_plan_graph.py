from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from sqlmodel import Session, select

from app.core.llm import LLMClient
from app.models.nursing import Elder, NursingProject
from app.prompts.agent import build_care_plan_prompt


class CarePlanState(TypedDict):
    elder_name: str
    care_goal: str
    plan: str


async def _build_care_plan(session: Session, elder_name: str, care_goal: str, llm: LLMClient) -> str:
    elder = session.exec(select(Elder).where(Elder.name == elder_name)).first()
    projects = list(session.exec(select(NursingProject)).all())

    if elder is None:
        return f"未找到老人 {elder_name} 的档案。"

    project_lines = "\n".join(
        f"- {project.name}：{project.description or project.category}"
        for project in projects[:12]
    ) or "暂无可选护理项目"
    prompt = build_care_plan_prompt(
        elder_name=elder.name,
        health_summary=elder.health_summary,
        care_goal=care_goal,
        project_lines=project_lines,
    )
    return await llm.chat(prompt)


def build_care_plan_graph(
    llm: LLMClient, session: Session
) -> CompiledStateGraph[CarePlanState, None, Any, CarePlanState]:
    async def generate(state: CarePlanState) -> CarePlanState:
        plan = await _build_care_plan(session, state["elder_name"], state["care_goal"], llm)
        return {"elder_name": state["elder_name"], "care_goal": state["care_goal"], "plan": plan}

    graph = StateGraph(CarePlanState)
    graph.add_node("generate", generate)
    graph.set_entry_point("generate")
    graph.add_edge("generate", END)
    return graph.compile()
