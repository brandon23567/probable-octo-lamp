from app.agent.state import AgentState
from app.agent.llm import generate_structured_content
from app.agent.schemas import ProjectPlan
import logging

logger = logging.getLogger("agent")

# async def plan_node(state: AgentState):
#     logger.info(f"Planning project: {state['project_name']}")
    
#     prompt = f"""
#     You are an expert software architect.
#     Plan a fullstack application for the following request:
#     "{state['user_prompt']}"
    
#     Project Name: {state['project_name']}
    
#     Requirements:
#     - Backend: FastAPI, SQLAlchemy, PostgreSQL, Pydantic.
#     - Frontend: React, TypeScript, Tailwind, Shadcn UI, React Query.
#     - Database: PostgreSQL with pgvector.
    
#     Output a structured JSON plan containing:
#     - backend_structure: List of file paths.
#     - frontend_structure: List of file paths.
#     - api_endpoints: List of dicts (method, path, description).
#     - database_models: List of dicts (name, description).
    
#     Ensure the structure is production-ready.
#     """
    
#     try:
#         plan = await generate_structured_content(prompt, ProjectPlan)
        
#         md_plan = f"# Project Plan: {plan.project_name}\n\n"
#         md_plan += f"## Description\n{plan.description}\n\n"
#         md_plan += "## Backend Structure\n" + "\n".join([f"- {f}" for f in plan.backend_structure, [])]) + "\n\n"
#         md_plan += "## API Endpoints\n" + "\n".join([f"- {e['method']} {e['path']}: {e['description']}" for e in plan.api_endpoints, [])]) + "\n\n"
        
#         state["project_plan_markdown"] = md_plan
        
#         return state
#     except Exception as e:
#         logger.error(f"Planning failed: {e}")
#         state["error_message"] = str(e)
#         return state


async def plan_node(state: AgentState):
    logger.info(f"Planning project: {state['project_name']}")
    
    prompt = f"""
    You are an expert software architect.
    Plan a fullstack application for the following request:
    "{state['user_prompt']}"
    
    Project Name: {state['project_name']}
    
    Requirements:
    - Backend: FastAPI, SQLAlchemy, PostgreSQL, Pydantic.
    - Frontend: React, TypeScript, Tailwind, Shadcn UI, React Query.
    - Database: PostgreSQL with pgvector.
    
    Ensure the structure is production-ready.
    """
    
    try:
        # 1. Get the parsed Pydantic object
        plan: ProjectPlan = await generate_structured_content(prompt, ProjectPlan)
        
        # 2. Build Markdown using object attribute access
        md_plan = f"# Project Plan: {plan.project_name}\n\n"
        
        # Using .get() style fallback isn't needed with Pydantic, 
        # but we use an empty list fallback just in case of Optional fields.
        
        md_plan += "## Backend Structure\n"
        backend_files = plan.backend_structure or []
        md_plan += "\n".join([f"- {f}" for f in backend_files]) + "\n\n"
        
        md_plan += "## Frontend Structure\n"
        frontend_files = plan.frontend_structure or []
        md_plan += "\n".join([f"- {f}" for f in frontend_files]) + "\n\n"
        
        md_plan += "## API Endpoints\n"
        endpoints = plan.api_endpoints or []
        # Accessing nested attributes as objects (e.method, not e['method'])
        md_plan += "\n".join([f"- **{e.method}** `{e.path}`: {e.description}" for e in endpoints]) + "\n\n"
        
        md_plan += "## Database Models\n"
        models = plan.database_models or []
        md_plan += "\n".join([f"- **{m.name}**: {m.description}" for m in models]) + "\n\n"
        
        # 3. Update State
        state["project_plan_markdown"] = md_plan
        return state

    except Exception as e:
        logger.error(f"Planning failed: {e}")
        state["error_message"] = str(e)
        return state