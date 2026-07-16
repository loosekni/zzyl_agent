from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.agents.chat_graph import build_chat_graph
from app.agents.checkin_graph import build_checkin_recommendation_graph
from app.core.database import get_session
from app.core.llm import LLMClient, get_llm_client
from app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    CheckInRecommendationRequest,
    CheckInRecommendationResponse,
)

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/chat", response_model=AgentChatResponse)
async def chat(request: AgentChatRequest, llm: LLMClient = Depends(get_llm_client)) -> AgentChatResponse:
    graph = build_chat_graph(llm)
    state = await graph.ainvoke({"message": request.message, "answer": ""})
    return AgentChatResponse(answer=state["answer"], conversation_id=request.conversation_id)


@router.post("/checkin/recommendation", response_model=CheckInRecommendationResponse)
async def recommend_checkin(
    request: CheckInRecommendationRequest,
    llm: LLMClient = Depends(get_llm_client),
    session: Session = Depends(get_session),
) -> CheckInRecommendationResponse:
    graph = build_checkin_recommendation_graph(llm, session)
    state = await graph.ainvoke({"elder_name": request.elder_name, "suggestion": ""})
    return CheckInRecommendationResponse(
        elder_name=state["elder_name"],
        suggestion=state["suggestion"],
    )
