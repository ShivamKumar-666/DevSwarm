# DevSwarm — Feature Ticket List

Format: `[ID] Title — Owner (suggested) — Phase — Priority`
Owner suggestions per the earlier ownership discussion: **Person A** = Orchestrator/RAG, Security, Incident (the novelty-claim path). **Person B** = Deploy, Monitor, Cost, Dashboard. Adjust to your actual agreed split.

## Phase 1 — Foundation
- **DS-001** Set up `docker-compose.yml` skeleton (Qdrant, Redis, Postgres placeholders) — Person B — P1 — Must
- **DS-002** FastAPI orchestrator app skeleton — Person A — P1 — Must
- **DS-003** Define `DevSwarmState` TypedDict schema — Person A — P1 — Must
- **DS-004** LangGraph `StateGraph` skeleton with event router stub — Person A — P1 — Must
- **DS-005** Agent stub files (all 5) with no-op tool calls — split — P1 — Must
- **DS-006** Repo structure + `.gitignore` + secret-scanning pre-commit hook — either — P1 — Must

## Phase 2 — MCP Integration (Deploy Agent E2E)
- **DS-010** Build github-mcp server (trigger_workflow, get_run_logs, create_pr_comment, merge_pr) — Person B — P2 — Must
- **DS-011** Build docker-mcp server (build_image, push_image, scan_image) — Person B — P2 — Must
- **DS-012** Build k8s-mcp server (apply_manifest, rollout_status, rollback_deployment, get_pods) — Person B — P2 — Must
- **DS-013** Stand up local `kind` cluster + `kind-cluster.yaml` — Person B — P2 — Must
- **DS-014** Deploy Agent: full push → build → deploy flow working E2E — Person B — P2 — Must
- **DS-015** Local Docker registry for image push/pull — Person B — P2 — Should

## Phase 3 — RAG Memory
- **DS-020** Qdrant client + collection setup (4 collections) — Person A — P3 — Must
- **DS-021** Embedding pipeline (BAAI/bge-large-en, local) — Person A — P3 — Must
- **DS-022** Decide + implement seed data source (real vs. synthetic) and disclosure metadata tag per record — Person A — P3 — Must
- **DS-023** Conflict resolver: retrieval + confidence scoring logic — Person A — P3 — Must (novelty claim — highest-priority ticket in the project)
- **DS-024** Orchestrator: escalation logic wired to confidence threshold — Person A — P3 — Must
- **DS-025** Decision logging back to Qdrant (closes the learning loop) — Person A — P3 — Must

## Phase 4 — Full Swarm
- **DS-030** prometheus-mcp server + self-hosted Prometheus/Grafana — Person B — P4 — Should
- **DS-031** Monitor Agent: anomaly scoring from Prometheus queries — Person B — P4 — Should
- **DS-032** security-mcp server (Trivy scan_image/scan_repo/get_cve_info, ZAP zap_scan) — Person A — P4 — Must
- **DS-033** Security Agent: block/allow verdict, PR comment on block — Person A — P4 — Must
- **DS-034** kubecost-mcp server (simulated pricing) — Person B — P4 — Should
- **DS-035** Cost Agent: right-sizing suggestion, explicit "simulated" tag on all output — Person B — P4 — Should
- **DS-036** Incident Agent: self-triggered webhook, precedent retrieval, remediation, GitHub issue creation — Person A — P4 — Must
- **DS-037** Deploy + Security parallel execution wired into Orchestrator — Person A — P4 — Must

## Phase 5 — Dashboard
- **DS-040** Next.js app scaffold — Person B — P5 — Must
- **DS-041** Agent Overview view — Person B — P5 — Must
- **DS-042** Decision Trail / timeline view (precedent + confidence display) — Person A or B (pairs well with novelty claim, consider pairing) — P5 — Must
- **DS-043** Human-Approval queue UI + action wired back to Qdrant logging — Person A — P5 — Must
- **DS-044** Live logs view with secret redaction — Person B — P5 — Must
- **DS-045** Cost simulation view with prominent "simulated" banner — Person B — P5 — Should
- **DS-046** WebSocket/polling data layer decision + implementation — Person B — P5 — Must

## Phase 6 — Polish, Report, Viva Prep
- **DS-050** Run Demo Scenario A (zero-touch deploy) E2E, fix gaps — both — P6 — Must
- **DS-051** Run Demo Scenario B (auto-incident response) E2E, fix gaps — both — P6 — Must
- **DS-052** Run Demo Scenario C (security gate) E2E, fix gaps — both — P6 — Must
- **DS-053** Record fallback demo video for all 3 scenarios — both — P6 — Must
- **DS-054** Write report: disclose Cost Agent simulation + Qdrant seed data provenance explicitly — both — P6 — Must
- **DS-055** Viva prep: each person can explain the full path for at least one scenario without notes — both — P6 — Must
- **DS-056** Security review pass (Security & Access Document §8 demo-day checklist) — both — P6 — Must
- **DS-057** Depth checkpoint per agent: each person explains the other's agent's failure modes without reading code — both — P6 — Should
