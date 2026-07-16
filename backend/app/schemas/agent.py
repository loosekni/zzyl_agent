from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class AgentChatResponse(BaseModel):
    answer: str
    conversation_id: str | None = None


class CheckInRecommendationRequest(BaseModel):
    elder_name: str = Field(min_length=1, max_length=64)


class CheckInRecommendationResponse(BaseModel):
    elder_name: str
    suggestion: str


class CarePlanRequest(BaseModel):
    elder_name: str = Field(min_length=1, max_length=64)
    care_goal: str = Field(default="", max_length=1000)


class CarePlanResponse(BaseModel):
    elder_name: str
    care_goal: str
    plan: str


class AlertAnalysisRequest(BaseModel):
    alert_id: int = Field(gt=0)


class AlertAnalysisResponse(BaseModel):
    alert_id: int
    analysis: str


class HealthProfileRequest(BaseModel):
    elder_id: int = Field(gt=0)


class AlertStatItem(BaseModel):
    severity: str
    count: int


class RecentAlertItem(BaseModel):
    device_name: str
    severity: str
    content: str
    created_at: str | None = None
    handled: bool = False


class TopDeviceItem(BaseModel):
    device_name: str
    count: int


class HealthProfileResponse(BaseModel):
    elder_id: int
    elder_name: str
    health_summary: str
    alert_total: int
    alert_stats: list[AlertStatItem]
    recent_alerts: list[RecentAlertItem]
    top_devices: list[TopDeviceItem]
    risk_score: int
    risk_level: str
    recommended_projects: list[str]
    summary: str
