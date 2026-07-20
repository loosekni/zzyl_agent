from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from sqlmodel import Session, select

from app.core.llm import LLMClient
from app.models.nursing import AlertRecord, Elder
from app.prompts.agent import build_alert_analysis_prompt


class AlertAnalysisState(TypedDict):
    alert_id: int
    analysis: str


async def _build_alert_analysis(session: Session, alert_id: int, llm: LLMClient) -> str:
    alert = session.get(AlertRecord, alert_id)

    if alert is None:
        return f"未找到 ID 为 {alert_id} 的告警记录。"

    elder = None
    if alert.elder_id is not None:
        elder = session.exec(select(Elder).where(Elder.id == alert.elder_id)).first()

    prompt = build_alert_analysis_prompt(
        device_name=alert.device_name,
        severity=alert.severity.value,
        content=alert.content,
        elder_name=elder.name if elder else None,
        health_summary=elder.health_summary if elder else None,
    )
    return await llm.chat(prompt)


def build_alert_analysis_graph(
    llm: LLMClient, session: Session
) -> CompiledStateGraph[AlertAnalysisState, None, Any, AlertAnalysisState]:
    async def analyze(state: AlertAnalysisState) -> AlertAnalysisState:
        analysis = await _build_alert_analysis(session, state["alert_id"], llm)
        return {"alert_id": state["alert_id"], "analysis": analysis}

    graph = StateGraph(AlertAnalysisState)
    graph.add_node("analyze", analyze)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", END)
    return graph.compile()
