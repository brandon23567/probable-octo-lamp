import os
import aiofiles
from pathlib import Path
from app.core.config import settings
import logging

logger = logging.getLogger("agent")

def validate_path(file_path: str, project_name: str, user_id: str) -> Path:
    """
    Strictly validates that the file_path is within the project directory.
    """
    project_root = Path(settings.PROJECTS_DIR) / user_id / project_name
    target_path = (project_root / file_path).resolve()
    
    # Security Check: Ensure strict containment
    if not str(target_path).startswith(str(project_root.resolve())):
        raise ValueError(f"Security Violation: Attempted to write outside project root: {target_path}")
    
    return target_path

async def write_file(file_path: str, content: str, project_name: str, user_id: str):
    try:
        target_path = validate_path(file_path, project_name, user_id)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(target_path, "w", encoding="utf-8") as f:
            await f.write(content)
        
        logger.info(f"File written: {target_path}")
    except ValueError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        raise

async def read_file(file_path: str, project_name: str, user_id: str) -> str:
    try:
        target_path = validate_path(file_path, project_name, user_id)
        if not target_path.exists():
            raise FileNotFoundError(f"File not found: {target_path}")
            
        async with aiofiles.open(target_path, "r", encoding="utf-8") as f:
            return await f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise
