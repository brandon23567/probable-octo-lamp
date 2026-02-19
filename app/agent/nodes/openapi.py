import asyncio
import subprocess
import httpx
import time
import os
import signal
from app.agent.state import AgentState
from app.core.config import settings
from app.agent.utils import write_file
import logging
from pathlib import Path

logger = logging.getLogger("agent")

async def extract_openapi_node(state: AgentState):
    logger.info("Extracting OpenAPI Schema...")
    
    project_root = Path(settings.PROJECTS_DIR) / state['user_id'] / state['project_name']
    backend_path = project_root / "backend"
    venv_path = backend_path / "venv"
    
    port = 8000
    
    # Use venv python
    if os.name == 'nt':
        python_executable = venv_path / "Scripts" / "python.exe"
    else:
        python_executable = venv_path / "bin" / "python"
        
    # Run uvicorn via python -m uvicorn
    cmd = [str(python_executable), "-m", "uvicorn", "main:app", "--port", str(port)]
    
    process = None
    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(backend_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        schema = None
        start_time = time.time()
        timeout = 20
        
        async with httpx.AsyncClient() as client:
            while time.time() - start_time < timeout:
                try:
                    response = await client.get(f"http://localhost:{port}/openapi.json")
                    if response.status_code == 200:
                        schema = response.json()
                        break
                except httpx.ConnectError:
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"Polling error: {e}")
                    await asyncio.sleep(1)
        
        if schema:
            logger.info("OpenAPI Schema fetched successfully.")
            import json
            schema_str = json.dumps(schema, indent=2)
            await write_file("openapi.json", schema_str, state['project_name'], state['user_id'])
            state["openapi_schema"] = schema
        else:
            logger.error("Failed to fetch OpenAPI schema within timeout.")
            state["error_message"] = "OpenAPI extraction timeout"
            state["build_status"] = "failed"
            
    except Exception as e:
        logger.error(f"OpenAPI extraction failed: {e}")
        state["error_message"] = str(e)
        state["build_status"] = "failed"
    finally:
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    
    return state
