import json

try:
    from qdrant_client import QdrantClient
except Exception as e:
    QdrantClient = None
    print(f"Warning: qdrant_client could not be imported: {e}")

def resolve_conflict(state: dict) -> dict:
    """
    RAG-based conflict resolution logic.
    Queries Qdrant for precedents.
    """
    if not state.get("conflict_flag"):
        state["final_decision"] = "proceed"
        return state

    print("[Conflict Resolver] Conflict detected. Querying Qdrant for precedents...")
    
    try:
        if QdrantClient is None:
            raise Exception("QdrantClient not available")
        
        client = QdrantClient(url="http://localhost:6333")
        client.set_model("BAAI/bge-small-en-v1.5")
        
        # Build a query string representing the current conflict
        # For MVP, we just take all agent outputs and stringify them
        agent_outputs = state.get("agent_outputs", {})
        query_text = "Conflict context: " + json.dumps(agent_outputs)
        
        # Determine which collection to search based on who voted to block/rollback
        collection_map = {
            "security": "past_security_scans",
            "cost": "cost_history",
            "incident": "past_incidents"
        }
        
        # Default fallback
        target_collection = "past_security_scans"
        
        for agent, agent_data in agent_outputs.items():
            vote = agent_data.get("vote", "")
            if vote in ("block", "rollback") and agent in collection_map:
                target_collection = collection_map[agent]
                # Keep looping to let the LAST agent (incident) take precedence, or we can just break.
                # Since incident is usually the most critical, let's just break for simplicity, but wait!
                # Actually, dicts preserve insertion order. Deploy -> Security -> Monitor -> Cost -> Incident.
                # So if security blocked, it breaks immediately. Let's NOT break, so it overwrites and prioritizes the later stages like cost/incident.
                
        print(f"[Conflict Resolver] Routing Qdrant query to collection: {target_collection}")
        
        # Save the target collection into state so the backend can write precedents back to the right place
        state["conflict_collection"] = target_collection
        
        search_result = client.query(
            collection_name=target_collection,
            query_text=query_text,
            limit=3
        )
        
        precedents = []
        highest_score = 0.0
        
        for hit in search_result:
            precedents.append({
                "document": hit.document,
                "metadata": hit.metadata,
                "score": hit.score
            })
            if hit.score > highest_score:
                highest_score = hit.score
                
        state["rag_context"] = precedents
        
        # Escalation Logic based on Confidence Score
        confidence_threshold = 0.80
        
        best_precedent = max(precedents, key=lambda precedent: precedent["score"], default=None)
        if best_precedent and highest_score >= confidence_threshold:
            decision = best_precedent["metadata"].get("decision", "escalate")
            print(f"[Conflict Resolver] High confidence precedent found (Score: {highest_score:.2f}). Applying automated resolution: {decision}")
            state["final_decision"] = decision
        else:
            print(f"[Conflict Resolver] Low confidence (Score: {highest_score:.2f}). Escalating to human.")
            state["final_decision"] = "escalate"

    except Exception as e:
        print(f"[Conflict Resolver] Error querying Qdrant: {e}. Defaulting to escalate.")
        state["final_decision"] = "escalate"
        state["rag_context"] = []
        
    return state
