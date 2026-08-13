from fastapi import FastAPI
from pydantic import BaseModel
from .graph import create_graph

app = FastAPI(title="DevSwarm Orchestrator")

graph = create_graph()

class EventPayload(BaseModel):
    event_type: str
    repo: str = ""
    commit_sha: str = ""

@app.get("/")
def health_check():
    return {"status": "ok", "service": "DevSwarm Orchestrator"}

@app.post("/events")
def ingest_event(payload: EventPayload):
    """
    Ingest events from external sources and route them into the LangGraph workflow.
    """
    initial_state = {
        "event_type": payload.event_type,
        "repo": payload.repo,
        "commit_sha": payload.commit_sha,
        "agent_outputs": {},
        "conflict_flag": False,
        "rag_context": [],
        "final_decision": "",
        "human_approval": False
    }
    
    # Run the graph synchronously for now
    final_state = graph.invoke(initial_state)
    
    return {"status": "processed", "state": final_state}
