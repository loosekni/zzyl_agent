from datetime import date

from pydantic import BaseModel, Field

from app.models.nursing import AlertSeverity, BedStatus, CheckInStatus, Gender


class ElderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    gender: Gender = Gender.unknown
    birthday: date | None = None
    phone: str | None = Field(default=None, max_length=32)
    family_contact: str | None = Field(default=None, max_length=64)
    health_summary: str | None = None


class RoomCreate(BaseModel):
    floor: str = Field(min_length=1, max_length=32)
    room_no: str = Field(min_length=1, max_length=32)
    room_type: str = Field(default="standard", max_length=64)


class BedCreate(BaseModel):
    room_id: int
    bed_no: str = Field(min_length=1, max_length=32)
    status: BedStatus = BedStatus.available


class NursingProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(default="daily", max_length=64)
    description: str | None = None
    price: float = 0


class AlertRecordCreate(BaseModel):
    elder_id: int | None = None
    device_name: str = Field(min_length=1, max_length=100)
    severity: AlertSeverity = AlertSeverity.medium
    content: str = Field(min_length=1)


class CheckInApplicationCreate(BaseModel):
    elder_id: int
    preferred_room_type: str | None = Field(default=None, max_length=64)
    care_needs: str | None = None
    status: CheckInStatus = CheckInStatus.draft
