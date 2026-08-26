from mcp_servers.kubecost_mcp.server import estimate_cost
from agents.llm_utils import ask_agent_to_vote
import json

def cost_node(state: dict):
    print("[Cost Agent] Estimating deployment cost...")
    deployment_name = state.get("deployment_name", "test-app")
    
    # 1. Run tool
    # For testing, let's request 2 cores and 4GB RAM to make it slightly expensive ($80)
    cost_result_str = estimate_cost(deployment_name=deployment_name, cpu_cores=2, memory_gb=4)
    print(f"[Cost Agent] Cost Result: {cost_result_str}")
    
    # 2. Get LLM Vote
    context = f"Here is the cost estimate: {cost_result_str}. If monthly_cost_usd > $50, you should probably vote 'block' due to budget constraints, otherwise 'proceed'."
    decision = ask_agent_to_vote("Cost Agent", context)
    print(f"[Cost Agent] Decision: {decision}")
    
    # 3. Update State
    state.setdefault("agent_outputs", {})["cost"] = {
        "status": "success",
        "cost_result": json.loads(cost_result_str),
        "vote": decision["vote"],
        "reason": decision["reason"]
    }
    return state
