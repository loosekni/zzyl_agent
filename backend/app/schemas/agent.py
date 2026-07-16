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


class AdmissionPreviewRequest(BaseModel):
    elder_id: int = Field(gt=0)
    preferred_bed_id: int | None = Field(default=None, gt=0)


class AdmissionPreviewResponse(BaseModel):
    run_id: int
    status: str
    elder_name: str
    bed_id: int
    bed_no: str
    preview_summary: str
    reservation_token: str
    expires_at: str


class AdmissionConfirmRequest(BaseModel):
    run_id: int = Field(gt=0)
    reservation_token: str = Field(min_length=1)


class AdmissionConfirmResponse(BaseModel):
    run_id: int
    status: str
    elder_id: int
    bed_id: int | None = None
    message: str


class AdmissionCancelRequest(BaseModel):
    run_id: int = Field(gt=0)
    reservation_token: str = Field(min_length=1)


class AdmissionCancelResponse(BaseModel):
    run_id: int
    status: str
    elder_id: int
    message: str
