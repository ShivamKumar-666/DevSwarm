# DevSwarm — Product Requirements Document (PRD)

## 1. Overview
DevSwarm is a swarm of five autonomous DevOps/SRE agents, orchestrated via LangGraph, wired to real tools through MCP servers, and grounded by a Qdrant-backed precedent memory. It manages deployment, monitoring, security scanning, cost estimation, and incident response for a containerized application, running entirely on free/local infrastructure (Docker Compose + `kind`).

**Core thesis / novelty claim:** precedent-based conflict resolution — when two agents disagree (e.g. Deploy wants to ship, Security flags a CVE), the Orchestrator retrieves the top-3 most similar past decisions from Qdrant, evaluates what worked, and proceeds or escalates to a human based on a confidence score. This is the project's primary research contribution and should anchor the report and viva.

## 2. Problem Statement
Manual DevOps/SRE work requires a human to correlate signals across deployment, monitoring, security, and cost tooling, and to remember how similar situations were handled before. DevSwarm automates that correlation and gives the system institutional memory via retrieval-augmented decision-making, instead of hardcoded rules.

## 3. Goals
- Demonstrate a working multi-agent system that makes non-trivial, precedent-informed decisions (not just scripted automation).
- Prove the MCP pattern: agents call real tools through standardized MCP servers rather than hardcoded API calls, so tools are swappable without touching agent logic.
- Ship three fully working, repeatable demo scenarios (deployment, incident response, security gate).
- Produce an honest, defensible academic report — explicitly disclosing what is simulated (Cost Agent pricing) and what is real (GitHub Actions, Trivy scans, kind cluster operations).

## 4. Non-Goals (v1)
- No real cloud infrastructure or billing (AWS, GCP) — zero-cost, local-only by design.
- No production-grade high availability, multi-tenant, or multi-cluster support.
- No custom LLM fine-tuning — uses Groq/Gemini free-tier inference as-is.
- No mobile app; dashboard is desktop-web only.

## 5. Users / Personas
- **SRE / on-call engineer (primary):** wants automated triage and remediation suggestions with human approval gate for risky actions.
- **Dev submitting a PR (secondary):** wants fast, explainable feedback when Security blocks a merge.
- **Grading panel / advisor (academic persona):** wants to see a working, explainable system and a clear novelty claim, defended live.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR1 | System ingests 4 event types: GitHub push, Prometheus alert, cron tick, CVE feed | Must |
| FR2 | Deploy Agent builds, scans (parallel with Security), and rolls out to a local `kind` cluster via k8s-mcp | Must |
| FR3 | Security Agent scans images/repos (Trivy) and can block a deploy | Must |
| FR4 | Incident Agent detects SLO/alert breaches, retrieves precedent from Qdrant, executes remediation, opens a GitHub issue | Must |
| FR5 | Orchestrator resolves agent conflicts via Qdrant precedent retrieval + confidence score; escalates below threshold | Must |
| FR6 | Monitor Agent surfaces anomaly scores from Prometheus | Should |
| FR7 | Cost Agent produces simulated right-sizing suggestions (Kubecost OSS, synthetic pricing) — explicitly labeled simulated everywhere it appears | Should |
| FR8 | Dashboard shows live agent status, decision trail, and a human-approval UI for escalated decisions | Must |
| FR9 | Every agent decision and Orchestrator resolution is logged to Qdrant/Postgres for future precedent retrieval | Must |
| FR10 | Three demo scenarios (A: zero-touch deploy, B: auto-incident response, C: security gate) run end-to-end and are recorded as a fallback | Must |

## 7. Success Metrics
- All 3 demo scenarios complete successfully live, with a recorded fallback available.
- Simulated MTTR reduction, false-positive rate of auto-remediation, and agent agreement/conflict rate reported with methodology explained.
- Every team member can independently explain the full decision path (event → agent → conflict resolution → outcome) for at least one demo scenario end-to-end in the viva.

## 8. Constraints
- 2 active contributors (of a 5-person roster), full-time availability.
- Zero budget — all infrastructure must run locally via Docker Compose / `kind`.
- 16-week timeline (see Project Phases Document).
- Report and viva must disclose: Cost Agent = simulated pricing; Qdrant seed data provenance (real vs. synthetic — decision pending).

## 9. Open Questions (carried over — resolve before/during Phase 1)
- Has the local-only, zero-cost scope been confirmed acceptable by the advisor/rubric?
- Final decision: real historical incident data vs. synthetic seed data for Qdrant, and how it will be disclosed in the report.
- Exact ownership split confirmed in writing (see Project Phases Document, §Ownership).
