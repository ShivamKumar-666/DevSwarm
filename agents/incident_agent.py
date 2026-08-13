def incident_node(state: dict):
    # Stub: Calls k8s-mcp, github-mcp
    state.setdefault("agent_outputs", {})["incident"] = {"status": "success", "message": "Incident stub executed"}
    return state
