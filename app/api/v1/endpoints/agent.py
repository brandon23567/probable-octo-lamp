from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.job import Job
from app.services.agent_service import run_agent_job
from app.db.session import get_db
from pydantic import BaseModel

router = APIRouter()

class JobRequest(BaseModel):
    project_name: str
    prompt: str

class JobResponseSchema(BaseModel):
    job_id: str
    status: str

@router.post("/start", response_model=JobResponseSchema)
def start_agent(
    request: JobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):

    job = Job(
        user_id=current_user.id,
        project_name=request.project_name,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    background_tasks.add_task(
        run_agent_job,
        str(job.id),
        request.prompt,
        current_user.id,
        request.project_name
    )
    
    return {"job_id": str(job.id), "status": "pending"}

@router.get("/status/{job_id}", response_model=JobResponseSchema)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):

    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": str(job.id), "status": job.status}
