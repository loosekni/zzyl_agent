from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.agents.alert_analysis_graph import AlertAnalysisState, build_alert_analysis_graph
from app.models.nursing import AlertRecord, AlertSeverity, Elder


class StubLLMClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    async def chat(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return f"分析结果：{prompt}"

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        yield await self.chat(prompt)


def _initial_state(alert_id: int) -> AlertAnalysisState:
    return {
        "alert_id": alert_id,
        "device_name": "",
        "severity": "",
        "content": "",
        "elder_name": "",
        "health_summary": "",
        "risk_route": "routine",
        "risk_summary": "",
        "analysis": "",
    }


def _session(tmp_path: Path) -> Session:
    engine = create_engine(f"sqlite:///{tmp_path / 'alert_graph.db'}")
    SQLModel.metadata.create_all(engine)
    return Session(engine)


@pytest.mark.anyio
async def test_alert_analysis_returns_friendly_message_when_missing(tmp_path: Path) -> None:
    llm = StubLLMClient()
    with _session(tmp_path) as session:
        graph = build_alert_analysis_graph(llm, session)
        state = await graph.ainvoke(_initial_state(999))

    assert state["analysis"] == "未找到 ID 为 999 的告警记录。"
    assert llm.prompts == []


@pytest.mark.anyio
async def test_alert_analysis_routes_medium_alert_to_routine_advice(tmp_path: Path) -> None:
    llm = StubLLMClient()
    with _session(tmp_path) as session:
        alert = AlertRecord(
            device_name="床垫传感器",
            severity=AlertSeverity.medium,
            content="离床时间较长",
        )
        session.add(alert)
        session.commit()
        session.refresh(alert)
        assert alert.id is not None

        graph = build_alert_analysis_graph(llm, session)
        state = await graph.ainvoke(_initial_state(alert.id))

    assert state["risk_route"] == "routine"
    assert "常规告警" in state["risk_summary"]
    assert "按常规护理流程" in llm.prompts[0]
    assert "床垫传感器" in state["analysis"]


@pytest.mark.anyio
async def test_alert_analysis_routes_critical_alert_to_urgent_advice(tmp_path: Path) -> None:
    llm = StubLLMClient()
    with _session(tmp_path) as session:
        elder = Elder(name="张桂兰", health_summary="高血压，近期跌倒风险高")
        session.add(elder)
        session.commit()
        session.refresh(elder)
        assert elder.id is not None

        alert = AlertRecord(
            elder_id=elder.id,
            device_name="紧急呼叫器",
            severity=AlertSeverity.critical,
            content="连续触发紧急呼叫",
        )
        session.add(alert)
        session.commit()
        session.refresh(alert)
        assert alert.id is not None

        graph = build_alert_analysis_graph(llm, session)
        state = await graph.ainvoke(_initial_state(alert.id))

    assert state["risk_route"] == "urgent"
    assert "高风险告警" in state["risk_summary"]
    assert "立即到场确认" in llm.prompts[0]
    assert "张桂兰" in llm.prompts[0]
