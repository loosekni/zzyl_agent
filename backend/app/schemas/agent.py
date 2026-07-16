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
