# DevSwarm — Technical Architecture Document

## 1. System Overview
DevSwarm is a five-agent system coordinated by a LangGraph-based Orchestrator, with each agent's tool access mediated by a dedicated MCP server. State is shared via a typed `DevSwarmState` object. Long-term memory lives in Qdrant; short-term/event transport uses Redis Streams. Everything runs via `docker-compose up`, with a local `kind` cluster as the deploy target.

## 2. High-Level Architecture

```
Event sources (GitHub webhook, Prometheus alert, cron, CVE feed)
        │
        ▼
   Orchestrator (LangGraph StateGraph)
     - Event router
     - Conflict resolver (RAG-based)
        │
   ┌────┼────┬────────┬─────────┐
   ▼    ▼    ▼        ▼         ▼
 Deploy Monitor Security  Cost   Incident
   │      │        │       │        │
github- prometheus- security- kubecost- k8s-mcp +
mcp     mcp         mcp       mcp       self-webhook
docker-
mcp
k8s-mcp
        │
        ▼
   Qdrant (4 collections) ── Redis Streams (event bus)
        │
        ▼
   Next.js SRE Dashboard (WebSocket/poll)
```

## 3. Components

### 3.1 Orchestrator
- **Framework:** LangGraph `StateGraph`, served via FastAPI.
- **Responsibilities:** route incoming events to the correct agent(s); run Deploy+Security in parallel where safe; detect conflicts between agent outputs; on conflict, query Qdrant for the 3 most similar precedent decisions, compute a confidence score, and decide `proceed` / `block` / `escalate`; log the final decision back to Qdrant for future retrieval.
- **State schema (`DevSwarmState`):**
```python
class DevSwarmState(TypedDict):
    event_type: str           # "push", "alert", "cron", "cve"
    repo: str
    commit_sha: str
    agent_outputs: dict        # {agent_name: output}
    conflict_flag: bool
    rag_context: list          # Retrieved precedent decisions
    final_decision: str        # "proceed", "block", "escalate"
    human_approval: bool
```

### 3.2 Agents
| Agent | Trigger | MCP tools | Output |
|---|---|---|---|
| Deploy | GitHub push/merge | github-mcp, docker-mcp, k8s-mcp | Rolling/canary deploy, rollback |
| Monitor | Cron / Alertmanager | prometheus-mcp | Anomaly score, metric snapshot |
| Security | Pre-deploy gate / CVE feed | security-mcp (Trivy + ZAP) | Vulnerability report, block/allow verdict |
| Cost | Daily scan / threshold | kubecost-mcp (simulated pricing) | Right-sizing suggestion (labeled simulated) |
| Incident | Self-triggered webhook / SLO breach | k8s-mcp, github-mcp | Auto-remediation, GitHub issue |

### 3.3 MCP Servers
Each MCP server is a thin FastAPI wrapper exposing a fixed tool interface over a free CLI/tool, so swapping the underlying tool never requires touching agent prompts or logic.

| Server | Tools exposed | Backing tool |
|---|---|---|
| github-mcp | trigger_workflow, get_run_logs, create_pr_comment, merge_pr | GitHub Actions API |
| docker-mcp | build_image, push_image, scan_image | Docker CLI + local registry |
| k8s-mcp | apply_manifest, rollout_status, rollback_deployment, get_pods | `kind` cluster |
| prometheus-mcp | query_range, get_alerts, silence_alert | self-hosted Prometheus + Grafana |
| kubecost-mcp | get_cost_estimate, get_rightsizing | Kubecost OSS against `kind` |
| security-mcp | scan_image, scan_repo, get_cve_info, zap_scan | Trivy + local OWASP ZAP |

### 3.4 RAG / Memory Layer
- **Vector DB:** Qdrant, local Docker container.
- **Embeddings:** BAAI/bge-large-en via local sentence-transformers (no external API dependency).
- **Collections:** `incident_runbooks`, `deployment_logs`, `security_patterns`, `cost_decisions`.
- **Retrieval flow:** an agent or the Orchestrator embeds the current situation's signature, retrieves top-3 nearest records, and includes them as `rag_context` for the decision step.
- **Seed data:** must be explicitly decided (real historical data vs. synthetic) and disclosed in the report — see Open Questions in the PRD.

### 3.5 Event Bus
Redis Streams (local Docker) carries events between trigger sources and the Orchestrator, decoupling event ingestion from agent execution.

### 3.6 Dashboard
- **Stack:** Next.js + Recharts.
- **Views:** live agent status, decision trail (including retrieved precedents and confidence scores), human-approval UI for escalated decisions, cost-simulation view (clearly labeled simulated).
- **Data path:** polls or subscribes via WebSocket to the orchestrator's FastAPI backend.

## 4. Data Flow — Example (Demo Scenario A: Zero-Touch Deploy)
1. GitHub push webhook → Orchestrator event router → Deploy path.
2. Deploy Agent (docker-mcp) builds image; Security Agent (security-mcp) scans in parallel.
3. Cost Agent (kubecost-mcp) estimates simulated cost impact.
4. If all pass: Deploy Agent applies manifest via k8s-mcp to `kind`.
5. Monitor Agent watches metrics for 5 minutes post-deploy.
6. All outputs logged to Qdrant `deployment_logs`; dashboard reflects green pipeline.

## 5. Infrastructure
- **Local orchestration:** `docker-compose.yml` brings up orchestrator, Qdrant, Redis, Prometheus, Grafana, and MCP servers.
- **Cluster:** `kind` (or `minikube`) via `kind-cluster.yaml`, no cloud account required.
- **CI:** GitHub Actions, public-repo free tier.
- **LLM inference:** Groq or Gemini free tier for agent reasoning calls.

## 6. Key Design Decisions
- **MCP over hardcoded API calls:** enforces a tool-swap boundary and is itself part of the novelty claim.
- **Precedent-based conflict resolution over hardcoded rules:** the system's core research contribution; must be implemented as genuine retrieval + confidence scoring, not a disguised if/else.
- **Zero-cost local infra:** removes cloud budget/access as a project risk, at the cost of not demonstrating real cloud billing or multi-node scale — disclose this tradeoff explicitly in the report.

## 7. Known Risks
- 6 custom MCP server wrappers is a large integration surface for 2 active contributors — track integration status per server explicitly (see Feature Ticket List).
- Live demo dependency on GitHub Actions, Trivy, and a local `kind` cluster all working simultaneously — mitigated by the recorded fallback demo (see Project Phases Document).
