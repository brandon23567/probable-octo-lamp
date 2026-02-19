import asyncio
from app.agent.state import AgentState
from app.agent.llm import generate_structured_content
from app.agent.schemas import FileGeneration
from app.agent.utils import write_file
import logging
from typing import List
from pydantic import BaseModel

logger = logging.getLogger("agent")

class FileList(BaseModel):
    files: List[FileGeneration]

async def generate_backend_node(state: AgentState):
    logger.info("Generating backend code...")
    
    prompt = f"""
    Generate the backend code for: {state['project_name']}
    
    PLAN:
    {state['project_plan_markdown']}
    
    Generate all necessary files based on this plan.
    Ensure 'requirements.txt' is included.
    Ensure 'main.py' is included.
    Ensure database configuration is included.
    
    Return a list of files with their content.
    """
    
    try:
        response_text = await generate_structured_content(prompt, FileList, model_name="gemini-2.5-flash") # Using flash for speed/cost or config default
        import json
        data = json.loads(response_text)
        files = data.get("files", [])
        
        generated_files = state.get("backend_files", {})
        
        for file in files:
            path = f"backend/{file['file_path']}" 

            if "backend/backend/" in path:
                path = path.replace("backend/backend/", "backend/")
            
            await write_file(path, file['code'], state['project_name'], state['user_id'])
            
            generated_files[path] = {
                "file_path": path,
                "content": file['code'],
                "status": "generated",
                "retry_count": 0,
                "last_error": None,
                "content_hash": None,
                "source": "llm"
            }
            
        state["backend_files"] = generated_files
        state["build_status"] = "pending"
        
        return state

    except Exception as e:
        logger.error(f"Backend generation failed: {e}")
        state["error_message"] = str(e)
        return state
