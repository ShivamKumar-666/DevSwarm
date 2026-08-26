from mcp.server.fastmcp import FastMCP
import subprocess
import json

mcp = FastMCP("security-mcp")

@mcp.tool()
def scan_image(image_tag: str) -> str:
    """
    Run a real Trivy vulnerability scan on a Docker image.
    Uses Docker to run aquasec/trivy to avoid needing local binary installation.
    """
    try:
        print(f"[Security MCP] Running Trivy scan on {image_tag}...")
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", "trivy-cache:/root/.cache/trivy",
                "aquasec/trivy", "image",
                "--format", "json",
                "--severity", "HIGH,CRITICAL",
                "--timeout", "5m",
                "--no-progress",
                image_tag
            ],
            capture_output=True,
            text=True,
            timeout=320,  # hard Python timeout
            check=False
        )
        
        if not result.stdout.strip():
            return json.dumps({
                "status": "error",
                "message": f"Trivy scan failed or returned empty output. stderr: {result.stderr[:500]}"
            })
            
        data = json.loads(result.stdout)
        summary = {"HIGH": 0, "CRITICAL": 0}
        cves = []
        
        results = data.get("Results", [])
        for res in results:
            vulnerabilities = res.get("Vulnerabilities", [])
            for vuln in vulnerabilities:
                severity = vuln.get("Severity")
                if severity in summary:
                    summary[severity] += 1
                    cves.append({
                        "pkg": vuln.get("PkgName"),
                        "cve": vuln.get("VulnerabilityID"),
                        "severity": severity,
                        "title": vuln.get("Title", "No title")
                    })
                    
        return json.dumps({
            "status": "success",
            "image": image_tag,
            "summary": summary,
            "top_cves": cves[:5]
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })
