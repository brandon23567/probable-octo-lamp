import asyncio
import subprocess
import os
import sys
from app.agent.state import AgentState
from app.core.config import settings
import logging
from pathlib import Path

logger = logging.getLogger("build")

async def build_backend_node(state: AgentState):
    logger.info("Building/Testing backend...")
    
    project_root = Path(settings.PROJECTS_DIR) / state['user_id'] / state['project_name']
    backend_path = project_root / "backend"
    
    venv_path = backend_path / "venv"
    
    # Windows paths
    if os.name == 'nt':
        python_executable = venv_path / "Scripts" / "python.exe"
        pip_executable = venv_path / "Scripts" / "pip.exe"
    else:
        python_executable = venv_path / "bin" / "python"
        pip_executable = venv_path / "bin" / "pip"

    try:
        # 1. Create Virtual Env
        if not venv_path.exists():
            logger.info("Creating virtual environment...")
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "venv", str(venv_path),
                cwd=str(backend_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if proc.returncode != 0:
                raise Exception("Failed to create venv")

        # 2. Install Requirements
        req_file = backend_path / "requirements.txt"
        if req_file.exists():
            logger.info("Installing requirements...")
            proc = await asyncio.create_subprocess_exec(
                str(python_executable), "-m", "pip", "install", "-r", "requirements.txt",
                cwd=str(backend_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            out, err = await proc.communicate()
            if proc.returncode != 0:
                logger.error(f"Pip install failed: {err.decode()}")
                raise Exception(f"Pip install failed: {err.decode()[-500:]}")
        
        # 3. Dry Run / Import Check (to ensure we can run uvicorn later)
        logger.info("Verifying backend imports...")
        proc = await asyncio.create_subprocess_exec(
            str(python_executable), "-c", "from main import app; print('Import successful')",
            cwd=str(backend_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
        
        if proc.returncode == 0:
            logger.info("Backend build successful.")
            state["build_status"] = "success"
            state["error_summary"] = None
        else:
            error_msg = err.decode()
            logger.error(f"Backend verification failed: {error_msg}")
            state["build_status"] = "failed"
            state["error_message"] = error_msg
            state["retry_count"] = state.get("retry_count", 0) + 1
            state["error_summary"] = error_msg[-2000:]

    except Exception as e:
        logger.error(f"Build process error: {e}")
        state["build_status"] = "failed"
        state["error_message"] = str(e)
        state["retry_count"] = state.get("retry_count", 0) + 1

    return state
