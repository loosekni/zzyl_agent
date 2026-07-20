from typing import TypedDict

from langchain_core.tools import BaseTool, tool
from sqlmodel import Session, select

from app.models.nursing import Bed, BedStatus, Elder, NursingProject


class ElderProfile(TypedDict):
    found: bool
    name: str
    health_summary: str


class BedAvailability(TypedDict):
    available_bed_count: int


class NursingProjectCatalog(TypedDict):
    nursing_project_count: int


def get_elder_profile(session: Session, elder_name: str) -> ElderProfile:
    elder = session.exec(select(Elder).where(Elder.name == elder_name)).first()
    if elder is None:
        return {"found": False, "name": elder_name, "health_summary": ""}
    return {
        "found": True,
        "name": elder.name,
        "health_summary": elder.health_summary or "无",
    }


def get_bed_availability(session: Session) -> BedAvailability:
    available_beds = list(session.exec(select(Bed).where(Bed.status == BedStatus.available)).all())
    return {"available_bed_count": len(available_beds)}


def get_nursing_project_catalog(session: Session) -> NursingProjectCatalog:
    projects = list(session.exec(select(NursingProject)).all())
    return {"nursing_project_count": len(projects)}


def build_checkin_context_tools(session: Session) -> list[BaseTool]:
    @tool("get_elder_profile")
    def elder_profile_tool(elder_name: str) -> ElderProfile:
        """Get an elder profile by exact elder name."""
        return get_elder_profile(session, elder_name)

    @tool("get_bed_availability")
    def bed_availability_tool() -> BedAvailability:
        """Count available beds for check-in recommendation."""
        return get_bed_availability(session)

    @tool("get_nursing_project_catalog")
    def nursing_project_catalog_tool() -> NursingProjectCatalog:
        """Count nursing projects that can be recommended."""
        return get_nursing_project_catalog(session)

    return [elder_profile_tool, bed_availability_tool, nursing_project_catalog_tool]
