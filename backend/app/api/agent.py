from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.agents.admission_agent import AdmissionAgent, AdmissionError
from app.agents.alert_analysis_graph import build_alert_analysis_graph
from app.agents.care_plan_graph import build_care_plan_graph
from app.agents.chat_graph import build_chat_graph
from app.agents.checkin_graph import build_checkin_recommendation_graph
from app.agents.health_profile_graph import build_health_profile_graph
from app.core.database import get_session
from app.core.llm import LLMClient, get_llm_client
from app.schemas.agent import (
    AdmissionCancelRequest,
    AdmissionCancelResponse,
    AdmissionConfirmRequest,
    AdmissionConfirmResponse,
    AdmissionPreviewRequest,
    AdmissionPreviewResponse,
    AgentChatRequest,
    AgentChatResponse,
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    CarePlanRequest,
    CarePlanResponse,
    CheckInRecommendationRequest,
    CheckInRecommendationResponse,
    HealthProfileRequest,
    HealthProfileResponse,
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


@router.post("/care-plan", response_model=CarePlanResponse)
async def generate_care_plan(
    request: CarePlanRequest,
    llm: LLMClient = Depends(get_llm_client),
    session: Session = Depends(get_session),
) -> CarePlanResponse:
    graph = build_care_plan_graph(llm, session)
    state = await graph.ainvoke(
        {"elder_name": request.elder_name, "care_goal": request.care_goal, "plan": ""}
    )
    return CarePlanResponse(
        elder_name=state["elder_name"],
        care_goal=state["care_goal"],
        plan=state["plan"],
    )


@router.post("/alert-analysis", response_model=AlertAnalysisResponse)
async def analyze_alert(
    request: AlertAnalysisRequest,
    llm: LLMClient = Depends(get_llm_client),
    session: Session = Depends(get_session),
) -> AlertAnalysisResponse:
    graph = build_alert_analysis_graph(llm, session)
    state = await graph.ainvoke({"alert_id": request.alert_id, "analysis": ""})
    return AlertAnalysisResponse(alert_id=state["alert_id"], analysis=state["analysis"])


@router.post("/health-profile", response_model=HealthProfileResponse)
async def health_profile(
    request: HealthProfileRequest,
    llm: LLMClient = Depends(get_llm_client),
    session: Session = Depends(get_session),
) -> HealthProfileResponse:
    graph = build_health_profile_graph(llm, session)
    state = await graph.ainvoke({"elder_id": request.elder_id})
    return HealthProfileResponse(**state)


@router.post("/admission/preview", response_model=AdmissionPreviewResponse)
async def admission_preview(
    request: AdmissionPreviewRequest,
    session: Session = Depends(get_session),
) -> AdmissionPreviewResponse:
    agent = AdmissionAgent(session)
    try:
        result = await agent.preview(request.elder_id, request.preferred_bed_id)
        return AdmissionPreviewResponse(**result)
    except AdmissionError as exc:
        raise HTTPException(
            status_code=400, detail={"code": exc.code, "message": str(exc)}
        ) from exc


@router.post("/admission/confirm", response_model=AdmissionConfirmResponse)
async def admission_confirm(
    request: AdmissionConfirmRequest,
    session: Session = Depends(get_session),
) -> AdmissionConfirmResponse:
    agent = AdmissionAgent(session)
    try:
        result = await agent.confirm(request.run_id, request.reservation_token)
        return AdmissionConfirmResponse(**result)
    except AdmissionError as exc:
        raise HTTPException(
            status_code=400, detail={"code": exc.code, "message": str(exc)}
        ) from exc


@router.post("/admission/cancel", response_model=AdmissionCancelResponse)
async def admission_cancel(
    request: AdmissionCancelRequest,
    session: Session = Depends(get_session),
) -> AdmissionCancelResponse:
    agent = AdmissionAgent(session)
    try:
        result = await agent.cancel(request.run_id, request.reservation_token)
        return AdmissionCancelResponse(**result)
    except AdmissionError as exc:
        raise HTTPException(
            status_code=400, detail={"code": exc.code, "message": str(exc)}
        ) from exc
