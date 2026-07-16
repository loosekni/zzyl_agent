"""老人健康风险画像 agent。

多节点编排：collect（采集档案与告警）→ score（计算风险评分）→ recommend（推荐护理项目并生成总结）。
纯数据驱动，不依赖外部 LLM 即可产出结构化画像；接入真实 LLM 后可在 recommend 节点增强总结。
"""

from collections import Counter
from datetime import datetime
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph
from sqlmodel import Session, select

from app.core.llm import LLMClient
from app.models.nursing import AlertRecord, AlertSeverity, Elder, NursingProject

# 告警级别权重：用于风险评分
_SEVERITY_WEIGHT: dict[AlertSeverity, int] = {
    AlertSeverity.low: 1,
    AlertSeverity.medium: 5,
    AlertSeverity.high: 12,
    AlertSeverity.critical: 25,
}

# 风险等级阈值
_RISK_LEVELS: list[tuple[int, str]] = [
    (80, "极高"),
    (50, "高"),
    (20, "中"),
    (0, "低"),
]

# 风险等级对应的推荐护理项目类别
_LEVEL_RECOMMEND: dict[str, list[str]] = {
    "极高": ["medical", "safety", "rehab"],
    "高": ["safety", "medical"],
    "中": ["safety", "daily"],
    "低": ["daily"],
}


class HealthProfileState(TypedDict, total=False):
    elder_id: int
    elder_name: str
    health_summary: str
    alert_total: int
    alert_stats: list[dict[str, Any]]
    recent_alerts: list[dict[str, Any]]
    top_devices: list[dict[str, Any]]
    risk_score: int
    risk_level: str
    recommended_projects: list[str]
    summary: str


def build_health_profile_graph(llm: LLMClient, session: Session):
    """构建健康风险画像 graph。llm 预留用于后续增强总结，当前为模板化生成。"""

    async def collect(state: HealthProfileState) -> HealthProfileState:
        elder_id = state["elder_id"]
        elder = session.get(Elder, elder_id)
        if elder is None:
            return {
                **state,
                "elder_name": "",
                "health_summary": "未找到该老人档案。",
                "alert_total": 0,
                "alert_stats": [],
                "recent_alerts": [],
                "top_devices": [],
            }

        alerts = list(
            session.exec(select(AlertRecord).where(AlertRecord.elder_id == elder_id)).all()
        )

        severity_counter: Counter[str] = Counter(a.severity.value for a in alerts)
        alert_stats = [
            {"severity": sev, "count": cnt}
            for sev, cnt in sorted(severity_counter.items(), key=lambda x: _severity_rank(x[0]))
        ]

        recent_alerts = [
            {
                "device_name": a.device_name,
                "severity": a.severity.value,
                "content": a.content,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "handled": a.handled,
            }
            for a in sorted(alerts, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]
        ]

        device_counter: Counter[str] = Counter(a.device_name for a in alerts)
        top_devices = [
            {"device_name": dev, "count": cnt}
            for dev, cnt in device_counter.most_common(3)
        ]

        return {
            **state,
            "elder_name": elder.name,
            "health_summary": elder.health_summary or "无",
            "alert_total": len(alerts),
            "alert_stats": alert_stats,
            "recent_alerts": recent_alerts,
            "top_devices": top_devices,
        }

    async def score(state: HealthProfileState) -> HealthProfileState:
        if not state.get("elder_name"):
            return {**state, "risk_score": 0, "risk_level": "未知"}

        stats = state.get("alert_stats", [])
        raw = sum(
            _SEVERITY_WEIGHT.get(AlertSeverity(item["severity"]), 0) * item["count"]
            for item in stats
        )
        risk_score = min(raw, 100)
        risk_level = "低"
        for threshold, level in _RISK_LEVELS:
            if risk_score >= threshold:
                risk_level = level
                break

        return {**state, "risk_score": risk_score, "risk_level": risk_level}

    async def recommend(state: HealthProfileState) -> HealthProfileState:
        if not state.get("elder_name"):
            return {**state, "recommended_projects": [], "summary": "未找到该老人档案，无法生成画像。"}

        risk_level = state["risk_level"]
        preferred_categories = _LEVEL_RECOMMEND.get(risk_level, ["daily"])
        projects = list(session.exec(select(NursingProject)).all())

        recommended: list[str] = []
        for category in preferred_categories:
            for project in projects:
                if project.category == category and project.name not in recommended:
                    recommended.append(project.name)
                    break

        # 模板化总结；预留 llm 入口，接入真实模型后可替换为 llm.chat 生成
        summary = _render_summary(state, recommended)
        _ = llm  # 预留：真实 LLM 接入后用 await llm.chat(prompt) 增强

        return {**state, "recommended_projects": recommended, "summary": summary}

    graph = StateGraph(HealthProfileState)
    graph.add_node("collect", collect)
    graph.add_node("score", score)
    graph.add_node("recommend", recommend)
    graph.set_entry_point("collect")
    graph.add_edge("collect", "score")
    graph.add_edge("score", "recommend")
    graph.add_edge("recommend", END)
    return graph.compile()


def _severity_rank(severity: str) -> int:
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return order.get(severity, 99)


def _render_summary(state: HealthProfileState, recommended: list[str]) -> str:
    name = state["elder_name"]
    total = state["alert_total"]
    level = state["risk_level"]
    score = state["risk_score"]
    health = state.get("health_summary", "无")
    top_devices = state.get("top_devices", [])

    device_text = (
        "、".join(f"{d['device_name']}({d['count']}次)" for d in top_devices)
        if top_devices
        else "暂无"
    )
    project_text = "、".join(recommended) if recommended else "暂无推荐"

    return (
        f"老人 {name} 当前健康风险等级为「{level}」（评分 {score}/100）。\n"
        f"健康摘要：{health}\n"
        f"累计告警 {total} 次，高频设备：{device_text}。\n"
        f"建议重点关注护理项目：{project_text}。"
    )
