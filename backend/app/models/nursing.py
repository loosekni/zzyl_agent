from datetime import date, datetime, timezone
from enum import StrEnum

from sqlmodel import Field, SQLModel


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
