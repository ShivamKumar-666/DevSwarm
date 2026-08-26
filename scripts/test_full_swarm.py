import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.graph import create_graph

def run_test():
    print("Initializing DevSwarm Full Swarm Test...")
    app = create_graph()
    
    # 1. Start a "push" event
    # We provide an image tag for security to scan. Nginx is usually clean or has known low-level vulns.
    # We use alpine so Trivy returns fast.
    initial_state = {
        "event_type": "push",
        "repo": "devswarm/test-app",
        "commit_sha": "abc1234",
        "image_tag": "nginx:1.14.2", 
        "deployment_name": "test-app",
        "agent_outputs": {}
    }
    
    print("\n--- Starting Execution ---")
    final_state = app.invoke(initial_state)
    
    print("\n--- Execution Complete ---")
    if final_state.get("conflict_flag"):
        print(f"Final Outcome: CONFLICT RESOLVED via Qdrant -> {final_state.get('final_decision')}")
    else:
        print(f"Final Outcome: UNANIMOUS -> {final_state.get('final_decision')}")

if __name__ == "__main__":
    run_test()
