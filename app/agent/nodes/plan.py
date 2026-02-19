from app.agent.state import AgentState
from app.agent.llm import generate_structured_content
from app.agent.schemas import ProjectPlan
import logging

logger = logging.getLogger("agent")

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
    
    Output a structured JSON plan containing:
    - backend_structure: List of file paths.
    - frontend_structure: List of file paths.
    - api_endpoints: List of dicts (method, path, description).
    - database_models: List of dicts (name, description).
    
    Ensure the structure is production-ready.
    """
    
    try:
        response_text = await generate_structured_content(prompt, ProjectPlan)
        # Assuming response_text is already JSON string of ProjectPlan because of structured output
        # But generate_structured_content implementation returns text. 
        # With new Gemini features it might be a valid JSON string.
        
        # We need to parse it or trust the LLM wrapper handling.
        # My llm.py implementation returns response.text.
        # If response_schema is used, Gemini returns JSON.
        
        import json
        plan_data = json.loads(response_text)
        
        # Convert to markdown for user review
        md_plan = f"# Project Plan: {plan_data.get('project_name')}\n\n"
        md_plan += f"## Description\n{plan_data.get('description')}\n\n"
        md_plan += "## Backend Structure\n" + "\n".join([f"- {f}" for f in plan_data.get('backend_structure', [])]) + "\n\n"
        md_plan += "## API Endpoints\n" + "\n".join([f"- {e['method']} {e['path']}: {e['description']}" for e in plan_data.get('api_endpoints', [])]) + "\n\n"
        
        state["project_plan_markdown"] = md_plan
        # Store structured data if needed, but state definition mainly has markdown for now.
        # We can add a 'plan' key to state if we want to keep the object.
        
        return state
    except Exception as e:
        logger.error(f"Planning failed: {e}")
        state["error_message"] = str(e)
        return state
