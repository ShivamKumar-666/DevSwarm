from qdrant_client import QdrantClient
import json

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
        client = QdrantClient(url="http://localhost:6333")
        client.set_model("BAAI/bge-small-en-v1.5")
        
        # Build a query string representing the current conflict
        # For MVP, we just take all agent outputs and stringify them
        query_text = "Conflict context: " + json.dumps(state.get("agent_outputs", {}))
        
        # We search across all collections, or a specific one depending on the context.
        # For simplicity, we just search 'past_security_scans' as an example if it's a security conflict.
        # A more robust system would route the query to the correct collection.
        # We'll just search 'past_security_scans' for the MVP demo.
        
        search_result = client.query(
            collection_name="past_security_scans",
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
        # (Assuming cosine similarity / fastembed score, where 1.0 is exact match)
        # Fastembed BGE small typically returns scores between 0.7 and 1.0 for related texts
        confidence_threshold = 0.85
        
        if highest_score >= confidence_threshold:
            print(f"[Conflict Resolver] High confidence precedent found (Score: {highest_score:.2f}). Applying automated resolution.")
            # In a real system, we'd apply the metadata action here
            state["final_decision"] = "proceed_based_on_precedent"
        else:
            print(f"[Conflict Resolver] Low confidence (Score: {highest_score:.2f} < {confidence_threshold}). Escalating to human.")
            state["final_decision"] = "escalate"

    except Exception as e:
        print(f"[Conflict Resolver] Error querying Qdrant: {e}. Defaulting to escalate.")
        state["final_decision"] = "escalate"
        state["rag_context"] = []
        
    return state
