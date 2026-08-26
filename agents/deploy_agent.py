from mcp_servers.docker_mcp.server import build_image, push_image
from mcp_servers.k8s_mcp.server import apply_manifest, check_rollout_status

def deploy_node(state: dict):
    # This is a basic integration simulating an agent deciding to use MCP tools.
    # In Phase 4, an LLM will actually choose to call these tools.
    
    # 1. Build the image
    build_result = build_image(dockerfile_path=".", tag="devswarm/test-app:latest")
    
    # 2. Deploy to K8s
    # (Assuming a k8s/deployment.yaml exists for testing)
    deploy_result = apply_manifest(manifest_path="k8s/deployment.yaml")
    
    # 3. Check status
    status_result = check_rollout_status(deployment_name="test-app-deployment")
    
    # Determine vote and reason based on actual results
    vote = "proceed"
    reason = "Deployed successfully"
    if "Error" in build_result or "Error" in deploy_result or "Error" in status_result:
        vote = "block"
        reason = "Deployment failed due to errors."
    elif "Rollout in progress" in status_result:
        vote = "monitor"
        reason = "Deployment applied but rollout is still in progress."

    state.setdefault("agent_outputs", {})["deploy"] = {
        "status": "success" if vote == "proceed" else "error", 
        "build_result": build_result,
        "deploy_result": deploy_result,
        "status_result": status_result,
        "vote": vote,
        "reason": reason
    }
    return state
