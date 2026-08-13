# DevSwarm — Agentic DevOps & SRE Platform
### Final Year Project — Complete Structure & Overview (Zero-Cost Edition)

---

## 1. One-Liner

A swarm of 5 autonomous DevOps agents — orchestrated by LangGraph, wired to real tools via MCP, and grounded by a Qdrant-backed precedent memory — that manages deployment, monitoring, security, cost, and incident response for a containerized app, entirely on free/local infrastructure.

---

## 2. Core Idea

Instead of one AI "doing DevOps," DevSwarm splits responsibility across five specialized agents that behave like a small SRE team. Each agent:

- watches for a specific trigger (a push, an alert, a cron tick, a CVE feed)
- has its own toolset, exposed as an **MCP server** (not hardcoded API calls — this is what makes it "agentic" rather than "scripted")
- writes its output to shared state
- can be overruled or paused by the **Orchestrator**, which resolves conflicts by retrieving similar past decisions from **Qdrant** before proceeding

The novelty isn't any single agent — it's the **precedent-based conflict resolution**: when Deploy wants to ship and Security flags a CVE, the system doesn't just hardcode a rule. It retrieves the 3 most similar past incidents, checks what worked, and decides with a confidence score. Below a threshold, it escalates to a human. That's your RAG contribution and your strongest thesis/report angle.

---

## 3. System Architecture

```
                         ┌─────────────────────────────┐
                         │        ORCHESTRATOR          │
                         │   (LangGraph StateGraph)     │
                         │  - Event router               │
                         │  - Conflict resolver           │
                         │  - RAG retrieval + decision    │
                         └───────────┬──────────────────┘
                                     │
        ┌──────────┬──────────┬─────┴─────┬──────────┬──────────┐
        ▼          ▼          ▼           ▼          ▼
   ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌───────────┐
   │ Deploy │ │Monitor │ │ Security │ │  Cost  │ │ Incident  │
   │ Agent  │ │ Agent  │ │  Agent   │ │ Agent  │ │  Agent    │
   └───┬────┘ └───┬────┘ └────┬─────┘ └───┬────┘ └─────┬─────┘
       │          │           │           │            │
       ▼          ▼           ▼           ▼            ▼
   github-mcp  prometheus- security-  kubecost-    k8s-mcp +
   docker-mcp  mcp          mcp        mcp (sim)    self-webhook
   k8s-mcp

                         ┌─────────────────────────────┐
                         │     QDRANT (local Docker)    │
                         │  - incident_runbooks         │
                         │  - deployment_logs           │
                         │  - security_patterns         │
                         │  - cost_decisions             │
                         └─────────────────────────────┘

                         ┌─────────────────────────────┐
                         │   Next.js SRE Dashboard       │
                         │  Live logs · agent status ·  │
                         │  approval UI · cost sim view │
                         └─────────────────────────────┘
```

Everything above runs on your laptop via Docker Compose + a local `kind` cluster. No cloud account required.

---

## 4. The 5 Agents

| Agent | Trigger | Tools (via MCP) | Output |
|---|---|---|---|
| **Deploy** | GitHub push / PR merge | github-mcp, docker-mcp, k8s-mcp (kind) | Rolling deploy, canary rollout, rollback |
| **Monitor** | Cron / Alertmanager webhook | prometheus-mcp (self-hosted) | Anomaly score, metric snapshots |
| **Security** | Pre-deploy gate / CVE feed | security-mcp (Trivy + local ZAP) | Vulnerability report, block/allow verdict |
| **Cost** | Daily scan / threshold breach | kubecost-mcp (simulated pricing) | Right-sizing suggestions, "estimated" savings |
| **Incident** | Self-triggered webhook / SLO breach | k8s-mcp, github-mcp | Auto-remediation, GitHub issue with root cause |

**Report language note:** Cost Agent output is a *simulation* (Kubecost OSS estimates against synthetic pricing since there's no real cloud bill) — say this explicitly in your report and viva rather than implying it's live AWS billing data.

---

## 5. MCP Server Mapping (Free Stack)

```
┌─────────────────────────────────────────────────────────────┐
│  MCP Server     │  Tools exposed                             │
├─────────────────────────────────────────────────────────────┤
│  github-mcp     │  trigger_workflow, get_run_logs,           │
│                  │  create_pr_comment, merge_pr               │
├─────────────────────────────────────────────────────────────┤
│  docker-mcp     │  build_image, push_image (local registry), │
│                  │  scan_image                                │
├─────────────────────────────────────────────────────────────┤
│  k8s-mcp         │  apply_manifest, rollout_status,           │
│                  │  rollback_deployment, get_pods (on kind)   │
├─────────────────────────────────────────────────────────────┤
│  prometheus-mcp  │  query_range, get_alerts, silence_alert    │
│                  │  (self-hosted Prometheus + Grafana)        │
├─────────────────────────────────────────────────────────────┤
│  kubecost-mcp    │  get_cost_estimate, get_rightsizing        │
│                  │  (Kubecost OSS against kind cluster)       │
├─────────────────────────────────────────────────────────────┤
│  security-mcp    │  scan_image (Trivy), scan_repo,            │
│                  │  get_cve_info, zap_scan (local ZAP)        │
└─────────────────────────────────────────────────────────────┘
```

Each MCP server is a thin FastAPI wrapper around a free CLI/tool — swapping tools later means touching the server, never the agent prompts.

---

## 6. LangGraph State Machine

```
Layer 1: Event Router
    ├── GitHub webhook   → Deploy path
    ├── Prometheus alert → Monitor → Incident path
    ├── Cron tick        → Cost path
    └── CVE feed         → Security path

Layer 2: Agent Execution (parallel where safe)
    Deploy + Security run in parallel (scan during build)
    Monitor + Cost are independent scheduled jobs

Layer 3: Conflict Resolution + RAG Retrieval
    └── If conflict → retrieve precedent from Qdrant → decide → log
```

```python
class DevSwarmState(TypedDict):
    event_type: str           # "push", "alert", "cron", "cve"
    repo: str
    commit_sha: str
    agent_outputs: dict       # {agent_name: output}
    conflict_flag: bool
    rag_context: list         # Retrieved precedent decisions
    final_decision: str       # "proceed", "block", "escalate"
    human_approval: bool
```

---

## 7. RAG Memory (Qdrant — local Docker)

| Collection | Content | Embedding |
|---|---|---|
| `incident_runbooks` | Past incident post-mortems, remediation steps | BAAI/bge-large-en (local, via sentence-transformers) |
| `deployment_logs` | Deployment outcomes, rollbacks, success/failure | same |
| `security_patterns` | CVE patterns, false-positive signatures | same |
| `cost_decisions` | Right-sizing actions, simulated savings | same |

Retrieval flow: Incident Agent sees "CPU spike + 502 errors" → embeds the signature → pulls top-3 similar past incidents → checks what worked → proposes the same fix before trying anything novel.

**Seed data matters here** — decide up front whether your Qdrant store starts with real historical incidents (from your own past projects/logs) or synthetic ones you generate, and disclose which in your report. Undisclosed synthetic seed data is the kind of thing that looks bad under viva questioning.

---

## 8. Tech Stack (Zero-Cost)

| Layer | Tech | Cost |
|---|---|---|
| Orchestrator | LangGraph + Python + FastAPI | Free |
| Agent LLM calls | Groq or Gemini (free tier) | Free |
| MCP servers | FastAPI + MCP SDK | Free |
| Vector DB | Qdrant (local Docker) | Free |
| Embeddings | BAAI/bge-large-en (local HF) | Free |
| Cluster | kind or minikube | Free |
| CI | GitHub Actions (public repo free tier) | Free |
| Monitoring | Prometheus + Grafana (self-hosted Docker) | Free |
| Security scan | Trivy + local OWASP ZAP | Free |
| Cost sim | Kubecost OSS | Free |
| Event bus | Redis Streams (local Docker) | Free |
| Dashboard | Next.js + Recharts | Free |
| Everything glued by | `docker-compose.yml` (+ kind as sidecar) | Free |

One command (`docker compose up`) should bring up the entire system for your demo — this is your whole infra story, and it sidesteps every question about cloud budget or shared dev clusters.

---

## 9. Repo / Folder Structure

```
devswarm/
├── docker-compose.yml            # spins up everything: qdrant, redis, prometheus, grafana, orchestrator
├── kind-cluster.yaml              # local k8s cluster config
├── orchestrator/
│   ├── main.py                    # FastAPI app entrypoint
│   ├── graph.py                   # LangGraph StateGraph definition
│   ├── state.py                   # DevSwarmState schema
│   ├── conflict_resolver.py       # RAG-based decision logic
│   └── event_router.py
├── agents/
│   ├── deploy_agent.py
│   ├── monitor_agent.py
│   ├── security_agent.py
│   ├── cost_agent.py
│   └── incident_agent.py
├── mcp_servers/
│   ├── github_mcp/
│   ├── docker_mcp/
│   ├── k8s_mcp/
│   ├── prometheus_mcp/
│   ├── kubecost_mcp/
│   └── security_mcp/
├── memory/
│   ├── qdrant_client.py
│   ├── seed_data/                 # incident/deployment/security/cost seed records
│   └── embeddings.py
├── dashboard/                     # Next.js app
│   ├── app/
│   ├── components/
│   └── api/
├── demo/
│   ├── scenario_a_deploy.md
│   ├── scenario_b_incident.md
│   ├── scenario_c_security_gate.md
│   └── recorded_backup/           # fallback demo recording — see §11
├── docs/
│   ├── architecture.md
│   ├── report_draft.md
│   └── viva_prep.md
└── tests/
```

---

## 10. Development Phases (16 Weeks)

| Phase | Weeks | Deliverable |
|---|---|---|
| P1: Foundation | 1–3 | FastAPI orchestrator skeleton, LangGraph state machine, agent stubs, docker-compose base |
| P2: MCP Integration | 4–6 | github-mcp, docker-mcp, k8s-mcp (against kind) — Deploy Agent working end-to-end |
| P3: RAG Memory | 7–9 | Qdrant live, 4 collections seeded, retrieval-augmented conflict resolution working |
| P4: Full Swarm | 10–12 | All 5 agents live, conflict resolution + vote mechanism, prometheus-mcp + kubecost-mcp + security-mcp |
| P5: Dashboard | 13–14 | Next.js dashboard, real-time WebSocket logs, human-approval UI |
| P6: Polish | 15–16 | Run all 3 demo scenarios end-to-end, record backup demo, write report, prep viva |

---

## 11. Demo Scenarios

**A — Zero-Touch Deployment:** push to main → Deploy builds image → Security scans (Trivy) → Cost estimates (Kubecost) → all pass → kind rollout via k8s-mcp → Monitor watches 5 min → dashboard shows green pipeline.

**B — Auto-Incident Response:** self-triggered webhook fires "memory leak" alert → Incident Agent retrieves similar past incident from Qdrant → executes pod restart via k8s-mcp → opens GitHub issue with root-cause hypothesis → human approves/rolls back in dashboard.

**C — Security Gate:** PR introduces a dependency with a known CVE → Security Agent blocks via Trivy scan → Orchestrator queries Qdrant for severity precedent → posts PR comment with fix suggestion → developer patches → re-run clears.

**Fallback plan:** record all 3 scenarios running successfully well before the viva. If a live MCP call, kind cluster, or webhook fails mid-demo, switch to the recording without missing a beat — don't try to debug live in front of graders.

---

## 12. Academic Framing

- **Novelty claim:** MCP-standardized tool access for an agentic DevOps swarm, fully reproducible without cloud infrastructure
- **Research contribution:** RAG-based precedent retrieval for automated conflict resolution and incident response
- **Evaluation metrics:** simulated MTTR reduction, false-positive rate of auto-remediation, agent agreement/conflict rate
- **Be upfront in the report about:** (1) Cost Agent uses simulated pricing, not live billing; (2) whether Qdrant seed data is real history or synthetic

---

## 13. Still Open (from your earlier checklist — not yet resolved)

- Team roster / individual ownership (this doc assumes solo build — update if that changes)
- Advisor requirements and actual grading rubric — mandatory vs. optional
- Which MCP servers you'll build yourself vs. find pre-built and stable
- Real vs. synthetic Qdrant seed data — decide and disclose
- Submission deliverables: report format, poster, demo format, deadlines
