def security_node(state: dict):
    # Stub: Calls security-mcp
    state.setdefault("agent_outputs", {})["security"] = {"status": "success", "message": "Security stub executed"}
    return state
