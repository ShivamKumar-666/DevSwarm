def cost_node(state: dict):
    # Stub: Calls kubecost-mcp
    state.setdefault("agent_outputs", {})["cost"] = {"status": "success", "message": "Cost stub executed (simulated)"}
    return state
