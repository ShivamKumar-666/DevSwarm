def monitor_node(state: dict):
    # Stub: Calls prometheus-mcp
    state.setdefault("agent_outputs", {})["monitor"] = {"status": "success", "message": "Monitor stub executed"}
    return state
