from typing import TypeVar

from fastapi import APIRouter, Depends
from sqlmodel import Session, SQLModel, select

from app.core.database import get_session
from app.models.nursing import AlertRecord, Bed, CheckInApplication, Elder, NursingProject, Room
from app.schemas.nursing import (
    AlertRecordCreate,
    BedCreate,
    CheckInApplicationCreate,
    ElderCreate,
    NursingProjectCreate,
    RoomCreate,
)

router = APIRouter(prefix="/nursing", tags=["nursing"])
ModelT = TypeVar("ModelT", bound=SQLModel)


def create_record(session: Session, record: ModelT) -> ModelT:
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("/elders", response_model=list[Elder])
def list_elders(session: Session = Depends(get_session)) -> list[Elder]:
    return list(session.exec(select(Elder)).all())


@router.post("/elders", response_model=Elder)
def create_elder(payload: ElderCreate, session: Session = Depends(get_session)) -> Elder:
    return create_record(session, Elder.model_validate(payload))


@router.get("/rooms", response_model=list[Room])
def list_rooms(session: Session = Depends(get_session)) -> list[Room]:
    return list(session.exec(select(Room)).all())


@router.post("/rooms", response_model=Room)
def create_room(payload: RoomCreate, session: Session = Depends(get_session)) -> Room:
    return create_record(session, Room.model_validate(payload))


@router.get("/beds", response_model=list[Bed])
def list_beds(session: Session = Depends(get_session)) -> list[Bed]:
    return list(session.exec(select(Bed)).all())


@router.post("/beds", response_model=Bed)
def create_bed(payload: BedCreate, session: Session = Depends(get_session)) -> Bed:
    return create_record(session, Bed.model_validate(payload))


@router.get("/projects", response_model=list[NursingProject])
def list_projects(session: Session = Depends(get_session)) -> list[NursingProject]:
    return list(session.exec(select(NursingProject)).all())


@router.post("/projects", response_model=NursingProject)
def create_project(payload: NursingProjectCreate, session: Session = Depends(get_session)) -> NursingProject:
    return create_record(session, NursingProject.model_validate(payload))


@router.get("/alerts", response_model=list[AlertRecord])
def list_alerts(session: Session = Depends(get_session)) -> list[AlertRecord]:
    return list(session.exec(select(AlertRecord)).all())


@router.post("/alerts", response_model=AlertRecord)
def create_alert(payload: AlertRecordCreate, session: Session = Depends(get_session)) -> AlertRecord:
    return create_record(session, AlertRecord.model_validate(payload))


@router.get("/checkins", response_model=list[CheckInApplication])
def list_checkins(session: Session = Depends(get_session)) -> list[CheckInApplication]:
    return list(session.exec(select(CheckInApplication)).all())


@router.post("/checkins", response_model=CheckInApplication)
def create_checkin(
    payload: CheckInApplicationCreate,
    session: Session = Depends(get_session),
) -> CheckInApplication:
    return create_record(session, CheckInApplication.model_validate(payload))
