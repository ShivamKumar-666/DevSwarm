from typing import TypedDict, Dict, Any, List

class DevSwarmState(TypedDict):
    """
    Core state object for the LangGraph Orchestrator.
    Passed between all nodes in the state graph.
    """
    event_type: str             # "push", "alert", "cron", "cve"
    repo: str
    commit_sha: str
    agent_outputs: Dict[str, Any]  # Store outputs from different agents
    conflict_flag: bool
    rag_context: List[Any]      # Retrieved precedent decisions from Qdrant
    final_decision: str         # "proceed", "block", "escalate"
    human_approval: bool
