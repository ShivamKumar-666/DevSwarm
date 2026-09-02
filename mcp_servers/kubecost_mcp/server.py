from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("kubecost-mcp")

@mcp.tool()
def estimate_cost(deployment_name: str, cpu_cores: int = 1, memory_gb: int = 1) -> str:
    """
    Mock Kubecost estimation.
    Returns simulated monthly cost based on requested resources.
    """
    # Simple simulated pricing: $30/core/month + $5/GB/month
    if cpu_cores < 0 or memory_gb < 0:
        return json.dumps({
            "status": "error",
            "message": "cpu_cores and memory_gb must be non-negative"
        })
        
    cpu_cost = cpu_cores * 30.0
    mem_cost = memory_gb * 5.0
    total_cost = cpu_cost + mem_cost
    
    # If cost exceeds $50, the agent might flag it as high
    return json.dumps({
        "status": "success",
        "deployment": deployment_name,
        "monthly_cost_usd": total_cost,
        "data_provenance": "simulated_pricing_for_demo",
        "breakdown": {
            "cpu_cost": cpu_cost,
            "memory_cost": mem_cost
        }
    })
