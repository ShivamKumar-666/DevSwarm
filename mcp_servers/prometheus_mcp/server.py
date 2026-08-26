from mcp.server.fastmcp import FastMCP
import json

mcp = FastMCP("prometheus-mcp")

@mcp.tool()
def query_metrics(metric_name: str, target: str = "default") -> str:
    """
    Mock Prometheus metric query.
    Returns simulated CPU and memory metrics for a given deployment or pod.
    """
    if "cpu" in metric_name.lower():
        # Simulated CPU spike to trigger an incident for the demo
        return json.dumps({
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "pod_cpu_usage_seconds_total", "pod": target},
                        "value": [1689304000, "0.95"] # 95% CPU usage
                    }
                ]
            }
        })
    elif "mem" in metric_name.lower():
        return json.dumps({
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [
                    {
                        "metric": {"__name__": "pod_memory_usage_bytes", "pod": target},
                        "value": [1689304000, "536870912"] # ~512MB
                    }
                ]
            }
        })
    
    return json.dumps({"status": "success", "data": {"result": []}})
