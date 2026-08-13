from langgraph.graph import StateGraph, END
from .state import DevSwarmState
from .event_router import route_event
from .conflict_resolver import resolve_conflict
from agents.deploy_agent import deploy_node
from agents.security_agent import security_node
from agents.monitor_agent import monitor_node
from agents.cost_agent import cost_node
from agents.incident_agent import incident_node

def create_graph() -> StateGraph:
    """
    Creates the main LangGraph StateGraph for DevSwarm orchestration.
    """
    workflow = StateGraph(DevSwarmState)
    
    # Add nodes
    workflow.add_node("deploy", deploy_node)
    workflow.add_node("security", security_node)
    workflow.add_node("monitor", monitor_node)
    workflow.add_node("cost", cost_node)
    workflow.add_node("incident", incident_node)
    workflow.add_node("conflict_resolver", resolve_conflict)
    
    # Set entry point
    workflow.set_entry_point("deploy") # Placeholder, usually we route conditionally
    
    # Conditional edge routing based on event_type can be set up here
    
    # Simple placeholder edges
    workflow.add_edge("deploy", "conflict_resolver")
    workflow.add_edge("security", "conflict_resolver")
    workflow.add_edge("conflict_resolver", END)
    
    return workflow.compile()
