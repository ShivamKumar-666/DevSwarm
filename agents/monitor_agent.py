from mcp_servers.prometheus_mcp.server import query_metrics
from agents.llm_utils import ask_agent_to_vote
import json

def monitor_node(state: dict):
    print("[Monitor Agent] Checking system health...")
    
    # 1. Run tool
    # Check CPU metrics
    metrics_str = query_metrics("pod_cpu_usage", target="test-app")
    print(f"[Monitor Agent] CPU Metrics: {metrics_str}")
    
    # 2. Get LLM Vote
    context = f"Here is the CPU metric data: {metrics_str}. If CPU usage > 0.8 (80%), vote 'monitor' or 'block', else vote 'proceed'."
    decision = ask_agent_to_vote("Monitor Agent", context)
    print(f"[Monitor Agent] Decision: {decision}")
    
    # 3. Update State
    state.setdefault("agent_outputs", {})["monitor"] = {
        "status": "success",
        "metrics": json.loads(metrics_str),
        "vote": decision["vote"],
        "reason": decision["reason"]
    }
    return state
