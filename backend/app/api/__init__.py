from fastapi import APIRouter

from app.api.agent import router as agent_router
from app.api.nursing import router as nursing_router

api_router = APIRouter()
api_router.include_router(agent_router)
api_router.include_router(nursing_router)
