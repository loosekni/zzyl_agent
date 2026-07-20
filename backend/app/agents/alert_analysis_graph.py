from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from sqlmodel import Session, select

from app.core.llm import LLMClient
from app.models.nursing import AlertRecord, AlertSeverity, Elder
from app.prompts.agent import build_alert_analysis_prompt

RiskRoute = Literal["routine", "urgent"]


class AlertAnalysisState(TypedDict):
    alert_id: int
    device_name: str
    severity: str
    content: str
    elder_name: str
    health_summary: str
    risk_route: RiskRoute
    risk_summary: str
    analysis: str


_URGENT_SEVERITIES: set[AlertSeverity] = {AlertSeverity.high, AlertSeverity.critical}


async def _collect_alert_context(session: Session, state: AlertAnalysisState) -> AlertAnalysisState:
    alert = session.get(AlertRecord, state["alert_id"])

    if alert is None:
        return {
            **state,
            "device_name": "",
            "severity": "",
            "content": "",
            "elder_name": "",
            "health_summary": "",
            "risk_route": "routine",
            "risk_summary": "未找到告警记录",
            "analysis": f"未找到 ID 为 {state['alert_id']} 的告警记录。",
        }

    elder = None
    if alert.elder_id is not None:
        elder = session.exec(select(Elder).where(Elder.id == alert.elder_id)).first()

    return {
        **state,
        "device_name": alert.device_name,
        "severity": alert.severity.value,
        "content": alert.content,
        "elder_name": elder.name if elder else "未关联",
        "health_summary": elder.health_summary if elder and elder.health_summary else "无",
        "risk_route": "routine",
        "risk_summary": "",
        "analysis": "",
    }


async def _grade_risk(state: AlertAnalysisState) -> AlertAnalysisState:
    if state["analysis"]:
        return state

    severity = AlertSeverity(state["severity"])
    if severity in _URGENT_SEVERITIES:
        return {
            **state,
            "risk_route": "urgent",
            "risk_summary": "高风险告警，需要立即确认老人状态并升级处理。",
        }
    return {
        **state,
        "risk_route": "routine",
        "risk_summary": "常规告警，建议护理人员按标准流程核查并记录处理结果。",
    }


async def _build_routine_advice(state: AlertAnalysisState, llm: LLMClient) -> AlertAnalysisState:
    if state["analysis"]:
        return state

    prompt = build_alert_analysis_prompt(
        device_name=state["device_name"],
        severity=state["severity"],
        content=state["content"],
        elder_name=state["elder_name"],
        health_summary=state["health_summary"],
        risk_summary=state["risk_summary"],
        response_focus="按常规护理流程给出处置建议，说明观察要点、记录要求和是否需要复查。",
    )
    return {**state, "analysis": await llm.chat(prompt)}


async def _build_urgent_advice(state: AlertAnalysisState, llm: LLMClient) -> AlertAnalysisState:
    if state["analysis"]:
        return state

    prompt = build_alert_analysis_prompt(
        device_name=state["device_name"],
        severity=state["severity"],
        content=state["content"],
        elder_name=state["elder_name"],
        health_summary=state["health_summary"],
        risk_summary=state["risk_summary"],
        response_focus="优先给出紧急处置步骤，包括立即到场确认、通知护士长/医生、联系家属和持续观察。",
    )
    return {**state, "analysis": await llm.chat(prompt)}


def _route_by_risk(state: AlertAnalysisState) -> RiskRoute:
    return state["risk_route"]


def build_alert_analysis_graph(
    llm: LLMClient, session: Session
) -> CompiledStateGraph[AlertAnalysisState, None, Any, AlertAnalysisState]:
    async def collect(state: AlertAnalysisState) -> AlertAnalysisState:
        return await _collect_alert_context(session, state)

    async def routine_advice(state: AlertAnalysisState) -> AlertAnalysisState:
        return await _build_routine_advice(state, llm)

    async def urgent_advice(state: AlertAnalysisState) -> AlertAnalysisState:
        return await _build_urgent_advice(state, llm)

    graph = StateGraph(AlertAnalysisState)
    graph.add_node("collect", collect)
    graph.add_node("grade_risk", _grade_risk)
    graph.add_node("routine_advice", routine_advice)
    graph.add_node("urgent_advice", urgent_advice)
    graph.set_entry_point("collect")
    graph.add_edge("collect", "grade_risk")
    graph.add_conditional_edges(
        "grade_risk",
        _route_by_risk,
        {"routine": "routine_advice", "urgent": "urgent_advice"},
    )
    graph.add_edge("routine_advice", END)
    graph.add_edge("urgent_advice", END)
    return graph.compile()
