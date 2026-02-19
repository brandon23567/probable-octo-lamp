from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

origins = [
    "http://localhost:3000",
    "http://localhost:8000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Coding Agent is running."}

@app.on_event("startup")
async def startup_event():
    import os

    os.makedirs(settings.PROJECTS_DIR, exist_ok=True)
    os.makedirs(settings.LOGS_DIR, exist_ok=True)

from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
