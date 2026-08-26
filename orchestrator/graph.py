from langgraph.graph import StateGraph, END
from .state import DevSwarmState
from agents.deploy_agent import deploy_node
from agents.security_agent import security_node
from agents.monitor_agent import monitor_node
from agents.cost_agent import cost_node
from agents.incident_agent import incident_node
from .conflict_resolver import resolve_conflict

def vote_evaluator(state: dict):
    print("\n[Vote Evaluator] Collecting votes from agents...")
    outputs = state.get("agent_outputs", {})
    votes = set()
    
    for agent_name, output in outputs.items():
        vote = output.get("vote")
        if vote:
            print(f" - {agent_name.capitalize()} Agent voted: {vote.upper()} (Reason: {output.get('reason')})")
            votes.add(vote)
            
    if len(votes) > 1:
        print("[Vote Evaluator] CONFLICT DETECTED! Mixed votes.")
        state["conflict_flag"] = True
    else:
        print(f"[Vote Evaluator] UNANIMOUS vote: {list(votes)[0].upper() if votes else 'NONE'}")
        state["conflict_flag"] = False
        decision = list(votes)[0] if votes else "no_agents"
        state["final_decision"] = decision
        
    return state

def should_resolve(state: dict):
    if state.get("conflict_flag"):
        return "conflict_resolver"
    return END

def route_after_deploy(state: dict):
    return ["security", "monitor", "cost", "incident"]

def create_graph() -> StateGraph:
    workflow = StateGraph(DevSwarmState)
    
    workflow.add_node("deploy", deploy_node)
    workflow.add_node("security", security_node)
    workflow.add_node("monitor", monitor_node)
    workflow.add_node("cost", cost_node)
    workflow.add_node("incident", incident_node)
    workflow.add_node("vote_evaluator", vote_evaluator)
    workflow.add_node("conflict_resolver", resolve_conflict)
    
    # Flow: deploy -> security -> monitor -> cost -> incident -> vote
    workflow.set_entry_point("deploy")
    workflow.add_edge("deploy", "security")
    workflow.add_edge("security", "monitor")
    workflow.add_edge("monitor", "cost")
    workflow.add_edge("cost", "incident")
    workflow.add_edge("incident", "vote_evaluator")
    
    workflow.add_conditional_edges("vote_evaluator", should_resolve, {
        "conflict_resolver": "conflict_resolver",
        END: END
    })
    
    workflow.add_edge("conflict_resolver", END)
    
    return workflow.compile()
