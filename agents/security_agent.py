from mcp_servers.security_mcp.server import scan_image
from agents.llm_utils import ask_agent_to_vote
import json

def security_node(state: dict):
    print("[Security Agent] Scanning image...")
    image_to_scan = state.get("image_tag")
    if not image_to_scan:
        state.setdefault("agent_outputs", {})["security"] = {
            "status": "error",
            "scan_result": "Error: No image_tag provided.",
            "vote": "block",
            "reason": "Missing image tag in state."
        }
        return state
    
    # 1. Run tool
    scan_result_str = scan_image(image_tag=image_to_scan)
    print(f"[Security Agent] Scan Result: {scan_result_str[:100]}...")
    
    # Parse result
    try:
        scan_result = json.loads(scan_result_str)
        is_success = isinstance(scan_result, dict) and scan_result.get("status") != "error"
    except Exception:
        scan_result = scan_result_str
        is_success = False

    if not is_success:
        state.setdefault("agent_outputs", {})["security"] = {
            "status": "error",
            "scan_result": scan_result,
            "vote": "block",
            "reason": "Security scan failed or returned invalid data."
        }
        return state
    
    # 2. Get LLM Vote
    decision = ask_agent_to_vote("Security Agent", scan_result_str)
    print(f"[Security Agent] Decision: {decision}")
    
    # 3. Update State
    state.setdefault("agent_outputs", {})["security"] = {
        "status": "success",
        "scan_result": scan_result,
        "vote": decision["vote"],
        "reason": decision["reason"]
    }
    return state
