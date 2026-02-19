from langgraph.graph import StateGraph, END
from app.agent.state import AgentState

# Placeholder Nodes
def plan_node(state: AgentState):
    return state

def human_review_node(state: AgentState):
    return state

def generate_backend_node(state: AgentState):
    return state

def build_backend_node(state: AgentState):
    return state

def fix_backend_node(state: AgentState):
    return state

def extract_openapi_node(state: AgentState):
    return state

def generate_frontend_node(state: AgentState):
    return state

def final_node(state: AgentState):
    return state

# Conditional Edges
def check_approval(state: AgentState):
    if state.get("approved"):
        return "generate_backend"
    return "human_review"

def check_build_status(state: AgentState):
    if state.get("build_status") == "success":
        return "extract_openapi"
    
    if state.get("retry_count", 0) < state.get("max_retries", 3):
        return "fix_backend"
    
    return "final" # Fail gracefully

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("plan", plan_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("generate_backend", generate_backend_node)
workflow.add_node("build_backend", build_backend_node)
workflow.add_node("fix_backend", fix_backend_node)
workflow.add_node("extract_openapi", extract_openapi_node)
workflow.add_node("generate_frontend", generate_frontend_node)
workflow.add_node("final", final_node)

workflow.set_entry_point("plan")

workflow.add_edge("plan", "human_review")

# Conditional edge from review
workflow.add_conditional_edges(
    "human_review",
    check_approval,
    {
        "generate_backend": "generate_backend",
        "human_review": "human_review"
    }
)

workflow.add_edge("generate_backend", "build_backend")

workflow.add_conditional_edges(
    "build_backend",
    check_build_status,
    {
        "extract_openapi": "extract_openapi",
        "fix_backend": "fix_backend",
        "final": "final"
    }
)

workflow.add_edge("fix_backend", "build_backend")
workflow.add_edge("extract_openapi", "generate_frontend")
workflow.add_edge("generate_frontend", "final")
workflow.add_edge("final", END)

app_graph = workflow.compile()
