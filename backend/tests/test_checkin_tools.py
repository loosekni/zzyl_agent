from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.agents.checkin_graph import RecommendationState, build_checkin_recommendation_graph
from app.models.nursing import Bed, BedStatus, Elder, NursingProject, Room
from app.tools.nursing import get_bed_availability, get_elder_profile, get_nursing_project_catalog


class StubLLMClient:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    async def chat(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return f"入住建议：{prompt}"

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        yield await self.chat(prompt)


def _session(tmp_path: Path) -> Session:
    engine = create_engine(f"sqlite:///{tmp_path / 'checkin_tools.db'}")
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def _initial_state(elder_name: str) -> RecommendationState:
    return {"elder_name": elder_name, "messages": [], "suggestion": ""}


def test_nursing_context_tools_query_business_data(tmp_path: Path) -> None:
    with _session(tmp_path) as session:
        elder = Elder(name="张桂兰", health_summary="高血压")
        room = Room(floor="2F", room_no="201")
        project = NursingProject(name="血压监测", category="medical")
        session.add(elder)
        session.add(room)
        session.add(project)
        session.commit()
        session.refresh(room)
        assert room.id is not None
        session.add(Bed(room_id=room.id, bed_no="201-1", status=BedStatus.available))
        session.add(Bed(room_id=room.id, bed_no="201-2", status=BedStatus.occupied))
        session.commit()

        assert get_elder_profile(session, "张桂兰") == {
            "found": True,
            "name": "张桂兰",
            "health_summary": "高血压",
        }
        assert get_bed_availability(session) == {"available_bed_count": 1}
        assert get_nursing_project_catalog(session) == {"nursing_project_count": 1}


@pytest.mark.anyio
async def test_checkin_graph_uses_tool_results_in_prompt(tmp_path: Path) -> None:
    llm = StubLLMClient()
    with _session(tmp_path) as session:
        elder = Elder(name="张桂兰", health_summary="高血压")
        room = Room(floor="2F", room_no="201")
        project = NursingProject(name="血压监测", category="medical")
        session.add(elder)
        session.add(room)
        session.add(project)
        session.commit()
        session.refresh(room)
        assert room.id is not None
        session.add(Bed(room_id=room.id, bed_no="201-1", status=BedStatus.available))
        session.commit()

        graph = build_checkin_recommendation_graph(llm, session)
        state = await graph.ainvoke(_initial_state("张桂兰"))

    assert "老人姓名：张桂兰" in llm.prompts[0]
    assert "健康摘要：高血压" in llm.prompts[0]
    assert "可用床位数：1" in llm.prompts[0]
    assert "护理项目数：1" in llm.prompts[0]
    assert state["suggestion"].startswith("入住建议：")


@pytest.mark.anyio
async def test_checkin_graph_does_not_call_llm_when_elder_missing(tmp_path: Path) -> None:
    llm = StubLLMClient()
    with _session(tmp_path) as session:
        graph = build_checkin_recommendation_graph(llm, session)
        state = await graph.ainvoke(_initial_state("不存在老人"))

    assert state["suggestion"] == "未找到老人 不存在老人 的档案。"
    assert llm.prompts == []
