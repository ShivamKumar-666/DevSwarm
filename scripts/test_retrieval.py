from sys import path
import os
import json

# Add project root to python path so we can import orchestrator
path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.conflict_resolver import resolve_conflict

def run_test():
    # Mocking a state where the Deploy Agent conflicts with the Security Agent
    # We'll simulate a security scan finding a medium severity vulnerability
    mock_state = {
        "conflict_flag": True,
        "agent_outputs": {
            "deploy": {"status": "success", "message": "Ready to deploy to staging"},
            "security": {"status": "blocked", "cve": "CVE-2023-222", "severity": "medium", "message": "Medium severity CVE found."}
        }
    }
    
    print("Testing RAG-based Conflict Resolver...")
    print(f"Incoming state: {json.dumps(mock_state, indent=2)}\n")
    
    result_state = resolve_conflict(mock_state)
    
    print(f"\nFinal Decision: {result_state.get('final_decision')}")
    print("RAG Context Retrieved:")
    for precedent in result_state.get('rag_context', []):
        print(f" - Score {precedent['score']:.4f}: {precedent['document']}")

if __name__ == "__main__":
    run_test()
