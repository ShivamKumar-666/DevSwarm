from mcp.server.fastmcp import FastMCP
from kubernetes import client, config
import yaml
import os

mcp = FastMCP("k8s-mcp")

# Initialize Kubernetes client (assumes local kubeconfig is set up, e.g., for kind)
try:
    config.load_kube_config()
    k8s_core_api = client.CoreV1Api()
    k8s_apps_api = client.AppsV1Api()
except Exception as e:
    k8s_core_api = None
    k8s_apps_api = None
    print(f"Warning: Could not connect to Kubernetes cluster: {e}")

@mcp.tool()
def apply_manifest(manifest_path: str, namespace: str = "default") -> str:
    """
    Applies a Kubernetes YAML manifest to the cluster.
    """
    if not k8s_core_api:
        return "Error: Kubernetes client not initialized."
    
    if not os.path.exists(manifest_path):
        return f"Error: Manifest file {manifest_path} not found."

    try:
        with open(manifest_path, 'r') as f:
            docs = yaml.safe_load_all(f)
            # A simplified apply logic. In a real scenario, kubernetes client utils
            # provides a create_from_yaml helper. For simplicity, we just mock success
            # or handle basic deployments.
            from kubernetes.utils import create_from_yaml
            k8s_client = client.ApiClient()
            create_from_yaml(k8s_client, manifest_path, namespace=namespace)
            
        return f"Successfully applied manifest: {manifest_path}"
    except Exception as e:
        return f"Error applying manifest: {str(e)}"

@mcp.tool()
def check_rollout_status(deployment_name: str, namespace: str = "default") -> str:
    """
    Checks the rollout status of a Kubernetes deployment.
    """
    if not k8s_apps_api:
        return "Error: Kubernetes client not initialized."
    try:
        deployment = k8s_apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        ready_replicas = deployment.status.ready_replicas or 0
        desired_replicas = deployment.spec.replicas
        
        if ready_replicas == desired_replicas:
            return f"Rollout successful. {ready_replicas}/{desired_replicas} replicas ready."
        else:
            return f"Rollout in progress. {ready_replicas}/{desired_replicas} replicas ready."
    except Exception as e:
        return f"Error checking rollout status: {str(e)}"

if __name__ == "__main__":
    mcp.run()
