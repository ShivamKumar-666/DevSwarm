from mcp_servers.security_mcp.server import scan_image
from agents.llm_utils import ask_agent_to_vote
import json

def security_node(state: dict):
    print("[Security Agent] Scanning image...")
    image_to_scan = state.get("image_tag", "nginx:latest") # Default to something scannable
    
    # 1. Run tool
    scan_result_str = scan_image(image_tag=image_to_scan)
    print(f"[Security Agent] Scan Result: {scan_result_str[:100]}...")
    
    # 2. Get LLM Vote
    decision = ask_agent_to_vote("Security Agent", scan_result_str)
    print(f"[Security Agent] Decision: {decision}")
    
    # 3. Update State
    state.setdefault("agent_outputs", {})["security"] = {
        "status": "success",
        "scan_result": json.loads(scan_result_str) if scan_result_str.startswith("{") else scan_result_str,
        "vote": decision["vote"],
        "reason": decision["reason"]
    }
    return state
