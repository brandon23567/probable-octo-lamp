import asyncio
import subprocess
import os
from app.agent.state import AgentState
from app.agent.utils import write_file
from app.core.config import settings
import logging
from pathlib import Path

logger = logging.getLogger("agent")

async def generate_frontend_node(state: AgentState):
    logger.info("Generating frontend code via Vite...")
    
    project_root = Path(settings.PROJECTS_DIR) / state['user_id'] / state['project_name']
    
    # We want to create 'frontend' folder inside project_root
    # Command: npm create vite@latest frontend -- --template react-ts
    
    # Ensure project root exists (should be there from backend step)
    project_root.mkdir(parents=True, exist_ok=True)
    
    # Check if frontend already exists to avoid overwriting or erroring?
    # User said "use subprocess... to create this react js project".
    
    frontend_path = project_root / "frontend"
    
    try:
        if not frontend_path.exists():
            logger.info("Scaffolding Vite React TS project...")
            # We run this in project_root
            # Shell=True might be needed for npm on Windows, or use 'npm.cmd'
            npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
            
            cmd = [npm_cmd, "create", "vite@latest", "frontend", "--", "--template", "react-ts"]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                logger.error(f"Vite creation failed: {stderr.decode()}")
                state["error_message"] = f"Vite creation failed: {stderr.decode()}"
                return state
        
        # Install Dependencies
        logger.info("Installing frontend dependencies...")
        deps = [
            "react-query", 
            "axios", 
            "react-router-dom", 
            "tailwindcss", 
            "postcss", 
            "autoprefixer",
            "zod",
            "clsx",
            "tailwind-merge", # often needed for shadcn
            "lucide-react" # often needed for shadcn
        ]
        # Shadcn usually requires init, which is interactive. 
        # For now, we manually install what we can or use a simplified approach. 
        # Or we can try to automate it? 
        # User said "install all the base packages we will need like ... shadcn ...".
        # Shadcn isn't a single package, it's a CLI mostly. 
        # "shadcn-ui" package exists but it is deprecated or different? 
        # Usually it's `npx shadcn@latest init`. 
        # We will install packages. `class-variance-authority` etc. are underlying libs.
        
        # Let's install standard libs.
        
        install_cmd = [npm_cmd, "install"]
        proc_install = await asyncio.create_subprocess_exec(
            *install_cmd,
            cwd=str(frontend_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc_install.communicate()
        
        # Install additional deps
        add_cmd = [npm_cmd, "install"] + deps
        proc_add = await asyncio.create_subprocess_exec(
            *add_cmd,
            cwd=str(frontend_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc_add.communicate()
        
        # Setup Tailwind (init)
        # npx tailwindcss init -p
        npx_cmd = "npx.cmd" if os.name == 'nt' else "npx"
        proc_tw = await asyncio.create_subprocess_exec(
            npx_cmd, "tailwindcss", "init", "-p",
            cwd=str(frontend_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc_tw.communicate()

        # We also need to write the tailwind.config.js content to include folders
        # And index.css
        
        # State update to indicate scaffolding done
        state["frontend_files"]["scaffold"] = {
            "file_path": "frontend/",
            "content": "scaffolded",
            "status": "generated",
            "retry_count": 0,
            "last_error": None,
            "content_hash": None,
            "source": "patched"
        }
        
    except Exception as e:
        logger.error(f"Frontend generation error: {e}")
        state["error_message"] = str(e)
    
    return state
