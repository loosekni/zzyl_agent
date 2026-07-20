from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from sqlmodel import Session, select

from app.core.llm import LLMClient
from app.models.nursing import AlertRecord, Elder


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

    prompt = (
        f"告警设备：{alert.device_name}\n"
        f"告警级别：{alert.severity}\n"
        f"告警内容：{alert.content}\n"
        f"老人姓名：{elder.name if elder else '未关联'}\n"
        f"健康摘要：{elder.health_summary if elder else '无'}\n"
        "请生成告警分析，包含可能原因、风险判断、护理处置建议和是否需要升级处理。"
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
