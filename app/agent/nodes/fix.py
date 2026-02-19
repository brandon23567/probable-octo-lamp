from app.agent.state import AgentState
from app.agent.llm import generate_structured_content
from app.agent.schemas import ErrorFixResponse
from app.agent.utils import write_file, read_file
from app.agent.memory import find_similar_error, store_error_memory
import logging
import re
import json

logger = logging.getLogger("agent")

async def fix_backend_node(state: AgentState):
    logger.info(f"Attempting valid fix... Retry {state.get('retry_count')}")
    
    error_msg = state.get("error_message")

    error_summary = state.get("error_summary") or error_msg[:2000]
    

    similar_memory = await find_similar_error(error_summary, threshold=0.85)
    if similar_memory:
        logger.info(f"Vector Memory Hit! Using stored fix for {similar_memory.file_path}")
        # Use stored corrected code
        target_file = similar_memory.file_path
        corrected_code = similar_memory.corrected_code
        
        await write_file(target_file, corrected_code, state['project_name'], state['user_id'])
        state["current_file"] = target_file

        return state

    prompt = f"""
    The backend build failed.
    Error: {error_msg}
    
    Analyze the traceback to find the specific file causing the error.
    
    Response Format:
    explanation: must start with 'FILE: relative/path/to/file.py' followed by the explanation.
    corrected_code: The full corrected code for that file.
    """
    
    try:
        response_text = await generate_structured_content(prompt, ErrorFixResponse)
        fix_data = json.loads(response_text)
        
        explanation = fix_data.get("explanation", "")
        corrected_code = fix_data.get("corrected_code", "")
        
        target_file = "backend/main.py"
        if "FILE: " in explanation:
            parts = explanation.split("FILE: ")[1].split("\n")[0].split(" ")[0]
            parts = parts.replace("'", "").replace('"', "")
            if parts.strip():
                if not parts.startswith("backend/"):
                    target_file = f"backend/{parts}"
                else:
                    target_file = parts

        await write_file(target_file, corrected_code, state['project_name'], state['user_id'])
        
        logger.info(f"Applied fix to {target_file}")
        state["current_file"] = target_file
        
        await store_error_memory(error_summary, target_file, corrected_code)
        
    except Exception as e:
        logger.error(f"Fix failed: {e}")
        state["build_status"] = "failed"
        
    return state
