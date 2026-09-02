from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import uuid
import datetime

# Add root directory to path to import orchestrator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orchestrator.graph import create_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import redis
import json
import re

def redact_secrets(text: str) -> str:
    if not isinstance(text, str):
        return text
    # Mask Groq API keys
    text = re.sub(r'gsk_[a-zA-Z0-9]{20,}', 'gsk_***REDACTED***', text)
    # Mask standard secret keys
    text = re.sub(r'sk-[a-zA-Z0-9]{20,}', 'sk-***REDACTED***', text)
    # Mask potential Github tokens
    text = re.sub(r'gh[pousr]_[a-zA-Z0-9]{36,}', 'ghp_***REDACTED***', text)
    return text

# Redis Stack Connection
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    # Ensure connection works
    redis_client.ping()
except Exception as e:
    print(f"Warning: Could not connect to Redis: {e}")
    redis_client = None

def get_run(run_id):
    if not redis_client:
        return None
    data = redis_client.json().get(f"run:{run_id}")
    return data if data else None

def set_run(run_id, data):
    if redis_client:
        redis_client.json().set(f"run:{run_id}", "$", data)

app_graph = create_graph()

class RunRequest(BaseModel):
    image_tag: str
    deployment_name: str

class ApprovalRequest(BaseModel):
    run_id: str
    decision: str

@app.post("/api/swarm/run")
def start_run(req: RunRequest, background_tasks: BackgroundTasks):
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis persistence is unavailable.")
    run_id = str(uuid.uuid4())
    run_data = {
        "status": "running",
        "logs": [],
        "state": None,
        "escalated": False,
        "start_time": datetime.datetime.utcnow().isoformat()
    }
    set_run(run_id, run_data)
    
    def run_swarm(r_id, image, dep):
        initial_state = {
            "event_type": "push",
            "repo": "devswarm/dashboard-test",
            "commit_sha": "abc1234",
            "image_tag": image, 
            "deployment_name": dep,
            "agent_outputs": {}
        }
        try:
            r_data = get_run(r_id) or {}
            r_data.setdefault("logs", []).append("[System] Starting swarm execution...")
            set_run(r_id, r_data)
            
            # Stream through the LangGraph nodes, capturing state after each one
            for output in app_graph.stream(initial_state):
                r_data = get_run(r_id) or {}
                for node_name, state_update in output.items():
                    # Merge incremental updates into the full state
                    if r_data.get("state") is None:
                        r_data["state"] = {}
                    r_data["state"].update(state_update)
                    
                    vote = state_update.get("agent_outputs", {}).get(node_name, {}).get("vote", "")
                    reason = state_update.get("agent_outputs", {}).get(node_name, {}).get("reason", "")
                    log_line = f"[{node_name}] Executed."
                    if vote:
                        log_line += f" Vote: {vote.upper()}. Reason: {reason}"
                    r_data["logs"].append(redact_secrets(log_line))
                    
                    # Check for escalation mid-stream
                    if state_update.get("final_decision") == "escalate":
                        r_data["status"] = "needs_approval"
                        r_data["escalated"] = True
                        r_data["logs"].append(redact_secrets("[System] Conflict unresolved — halted for human approval."))
                set_run(r_id, r_data)
            
            # Check final decision if not already escalated
            r_data = get_run(r_id) or {}
            if r_data.get("status") == "running":
                final_state = r_data.get("state") or {}
                final_decision = final_state.get("final_decision")
                if final_decision == "escalate":
                    r_data["status"] = "needs_approval"
                    r_data["escalated"] = True
                    r_data["logs"].append(redact_secrets("[System] Swarm halted for human approval."))
                else:
                    r_data["status"] = "completed"
                    r_data["logs"].append(redact_secrets(f"[System] Swarm finished: {final_decision}"))
                set_run(r_id, r_data)
        except Exception as e:
            # Even on error, check if we already have a valid escalated state
            r_data = get_run(r_id) or {}
            partial_state = r_data.get("state") or {}
            if partial_state.get("final_decision") == "escalate":
                r_data["status"] = "needs_approval"
                r_data["escalated"] = True
                r_data["logs"].append(redact_secrets("[System] Swarm halted for human approval."))
            else:
                r_data["status"] = "failed"
                r_data["logs"].append(redact_secrets(f"[Error] {str(e)}"))
            set_run(r_id, r_data)

    background_tasks.add_task(run_swarm, run_id, req.image_tag, req.deployment_name)
    return {"run_id": run_id}

@app.get("/api/swarm/status/{run_id}")
def get_status(run_id: str):
    data = get_run(run_id)
    return data if data else {"error": "not found"}

@app.get("/api/swarm/queue")
def get_queue():
    queue = []
    if redis_client:
        keys = redis_client.keys("run:*")
        for key in keys:
            data = redis_client.json().get(key)
            if data and data.get("escalated"):
                r_id = key.split(":")[1]
                queue.append({"run_id": r_id, "state": data["state"]})
    return {"queue": queue}

@app.post("/api/swarm/approve")
def approve_action(req: ApprovalRequest):
    run_id = req.run_id
    r_data = get_run(run_id)
    if not r_data:
        return {"status": "error", "message": f"run {run_id[:8]} not found in Redis"}
    if r_data["status"] not in ("escalated", "needs_approval"):
        return {"status": "error", "message": f"run status is '{r_data['status']}', not escalated"}
    
    r_data["status"] = "completed"
    r_data["escalated"] = False
    if r_data["state"] is None:
        r_data["state"] = {}
    r_data["state"]["final_decision"] = req.decision
    r_data["state"]["human_approval"] = req.decision
    r_data["logs"].append(redact_secrets(f"[System] Human intervened: {req.decision}"))
    
    conflict_collection = r_data["state"].get("conflict_collection", "past_security_scans")
    
    # Save precedent back to Qdrant to close the learning loop
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url="http://localhost:6333")
        client.set_model("BAAI/bge-small-en-v1.5")
        import uuid as uid
        
        # Build rich precedent context
        image_tag = r_data.get("state", {}).get("image_tag", "unknown")
        agent_outputs = r_data.get("state", {}).get("agent_outputs", {})
        context_str = f"Image {image_tag} was flagged. "
        for agent, output in agent_outputs.items():
            if isinstance(output, dict) and "vote" in output:
                context_str += f"{agent} voted {output['vote']} because: {output.get('reason', 'no reason')}. "
        precedent_doc = f"{context_str}Human manually chose to {req.decision}."
        
        client.add(
            collection_name=conflict_collection,
            documents=[precedent_doc],
            metadata=[{"decision": req.decision, "human_override": True}],
            ids=[uid.uuid4().int & (1<<64)-1]
        )
        r_data["logs"].append(redact_secrets(f"[System] Precedent saved to Qdrant collection: {conflict_collection}."))
    except Exception as e:
        r_data["logs"].append(redact_secrets(f"[System Error] Failed saving precedent: {e}"))
        
    set_run(run_id, r_data)
    return {"status": "success", "decision": req.decision}
