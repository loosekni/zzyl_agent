from datetime import date, datetime, timezone
from enum import StrEnum

from sqlmodel import Field, SQLModel


class MessageRole(StrEnum):
    user = "user"
    assistant = "assistant"


class ConversationRecord(SQLModel, table=True):
    id: str = Field(primary_key=True, max_length=64)
    title: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversationrecord.id", index=True, max_length=64)
    role: MessageRole = Field(index=True)
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


class Gender(StrEnum):
    male = "male"
    female = "female"
    unknown = "unknown"


class BedStatus(StrEnum):
    available = "available"
    occupied = "occupied"
    maintenance = "maintenance"


class AlertSeverity(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class CheckInStatus(StrEnum):
    draft = "draft"
    reviewing = "reviewing"
    approved = "approved"
    rejected = "rejected"


class Elder(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=64)
    gender: Gender = Field(default=Gender.unknown)
    birthday: date | None = None
    phone: str | None = Field(default=None, max_length=32)
    family_contact: str | None = Field(default=None, max_length=64)
    health_summary: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Room(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    floor: str = Field(index=True, max_length=32)
    room_no: str = Field(index=True, max_length=32)
    room_type: str = Field(default="standard", max_length=64)


class Bed(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="room.id", index=True)
    bed_no: str = Field(max_length=32)
    status: BedStatus = Field(default=BedStatus.available)


class NursingProject(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    category: str = Field(default="daily", max_length=64)
    description: str | None = None
    price: float = Field(default=0)


class AlertRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    elder_id: int | None = Field(default=None, foreign_key="elder.id", index=True)
    device_name: str = Field(max_length=100)
    severity: AlertSeverity = Field(default=AlertSeverity.medium)
    content: str
    handled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CheckInApplication(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    elder_id: int = Field(foreign_key="elder.id", index=True)
    preferred_room_type: str | None = Field(default=None, max_length=64)
    care_needs: str | None = None
    status: CheckInStatus = Field(default=CheckInStatus.draft)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdmissionStatus(StrEnum):
    idle = "IDLE"
    running = "RUNNING"
    waiting_approval = "WAITING_APPROVAL"
    completed = "COMPLETED"
    cancelled = "CANCELLED"
    expired = "EXPIRED"
    failed = "FAILED"


class AdmissionRun(SQLModel, table=True):
    """入住办理 Agent 的有状态运行记录。简化版用 SQLite 持久化替代原项目的 Redis checkpoint。"""

    id: int | None = Field(default=None, primary_key=True)
    elder_id: int = Field(foreign_key="elder.id", index=True)
    status: AdmissionStatus = Field(default=AdmissionStatus.waiting_approval, index=True)
    reservation_token: str | None = Field(default=None, index=True)
    expires_at: datetime | None = None
    bed_id: int | None = Field(default=None, foreign_key="bed.id")
    preview_summary: str | None = None
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
