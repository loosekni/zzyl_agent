from fastapi import APIRouter, Depends

from app.agents.chat_graph import build_chat_graph
from app.core.llm import LLMClient, get_llm_client
from app.schemas.agent import AgentChatRequest, AgentChatResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/chat", response_model=AgentChatResponse)
async def chat(request: AgentChatRequest, llm: LLMClient = Depends(get_llm_client)) -> AgentChatResponse:
    graph = build_chat_graph(llm)
    state = await graph.ainvoke({"message": request.message, "answer": ""})
    return AgentChatResponse(answer=state["answer"], conversation_id=request.conversation_id)
