import asyncio
from app.models.job import Job, JobStatus
from app.agent.graph import app_graph
from app.agent.state import AgentState
from app.core.config import settings
import logging

logger = logging.getLogger("agent")


async def run_agent_job(job_id: str, prompt: str, user_id: int, project_name: str):
    logger.info(f"Starting job {job_id} for project {project_name}")
    
    try:

        initial_state: AgentState = {
            "user_prompt": prompt,
            "user_id": str(user_id),
            "project_name": project_name,
            "project_root": "", 
            "project_plan_markdown": "",
            "tech_stack": {},
            "approved": True, 
            "backend_files": {},
            "frontend_files": {},
            "current_file": None,
            "error_message": None,
            "error_summary": None,
            "retry_count": 0,
            "max_retries": 5, 
            "build_status": "pending",
            "iteration_count": 0
        }
        
        result = await app_graph.ainvoke(initial_state)
        
        from app.db.session import SessionLocal
        job_db = SessionLocal()
        try:
            job = job_db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = JobStatus.COMPLETED
                job.result_summary = "Completed successfully" 
                job_db.commit()
                logger.info(f"Job {job_id} completed.")
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
        finally:
            job_db.close()
            
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        from app.db.session import SessionLocal
        job_db = SessionLocal()
        try:
            job = job_db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.result_summary = str(e)
                job_db.commit()
        finally:
            job_db.close()
