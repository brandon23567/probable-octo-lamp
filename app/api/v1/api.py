from app.api.v1.endpoints import auth, agent
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
