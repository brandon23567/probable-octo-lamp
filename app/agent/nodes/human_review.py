from app.agent.state import AgentState

def human_review_node(state: AgentState):
    # This node doesn't do much automatically.
    # It acts as a pause point in the graph where strict "interrupt" might be used in LangGraph.
    # For now, we just pass state. The external API will check 'approved' flag.
    return state
