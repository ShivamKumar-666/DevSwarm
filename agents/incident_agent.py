from mcp_servers.prometheus_mcp.server import query_metrics
from agents.llm_utils import ask_agent_to_vote
import json

def incident_node(state: dict):
    print("[Incident Agent] Checking for active incidents or anomalies...")
    
    # 1. Run tool
    # Check memory metrics
    target_app = state.get("deployment_name", "test-app")
    metrics_str = query_metrics("pod_mem_usage", target=target_app)
    print(f"[Incident Agent] Memory Metrics: {metrics_str}")
    
    # 2. Get LLM Vote
    context = f"Here is the Memory metric data: {metrics_str}. If there are huge spikes or memory > 500MB, vote 'rollback', else vote 'proceed'."
    decision = ask_agent_to_vote("Incident Agent", context)
    print(f"[Incident Agent] Decision: {decision}")
    
    # 3. Update State
    state.setdefault("agent_outputs", {})["incident"] = {
        "status": "success",
        "metrics": json.loads(metrics_str),
        "vote": decision["vote"],
        "reason": decision["reason"]
    }
    return state
