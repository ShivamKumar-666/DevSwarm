# DevSwarm — Project Phases Document

## Team & Ownership (confirm in writing before Phase 1 starts)
- 2 active contributors of a 5-person roster.
- Suggested split, mapped to the novelty claim: **Person A** owns Orchestrator, RAG/conflict resolution, Security Agent, Incident Agent — the precedent-retrieval path that is the project's core research contribution. **Person B** owns Deploy Agent, Monitor Agent, Cost Agent, and the Dashboard.
- Each person should have commits reflecting their owned components specifically — not merged/shared commits — so individual contribution is demonstrable if questioned.
- This split should be confirmed with your advisor if the rubric evaluates individual contribution separately from team output.

## Phase 1 — Foundation (Weeks 1–3)
**Deliverable:** FastAPI orchestrator skeleton, LangGraph state machine, agent stubs, docker-compose base.
- Repo structure, `.gitignore`, secret-scanning hook
- `DevSwarmState` schema defined
- Event router stub (all 4 event types recognized, routed to stub handlers)
- All 5 agent files exist as no-op stubs

## Phase 2 — MCP Integration (Weeks 4–6)
**Deliverable:** github-mcp, docker-mcp, k8s-mcp working — Deploy Agent functional end-to-end.
- Local `kind` cluster running
- Push → build → scan → deploy flow works for a real (simple) containerized app
- This phase is the first real proof the MCP pattern works — don't skip validating that tool-swapping actually works without touching agent code, since that's part of the novelty claim.

## Phase 3 — RAG Memory (Weeks 7–9)
**Deliverable:** Qdrant live, 4 collections seeded, retrieval-augmented conflict resolution working.
- Seed data source decided and disclosed (real vs. synthetic)
- Conflict resolver implemented as genuine retrieval + confidence scoring — this is the highest-priority technical component in the whole project
- Orchestrator escalation logic wired to a documented, justified confidence threshold

## Phase 4 — Full Swarm (Weeks 10–12)
**Deliverable:** All 5 agents live, conflict resolution + vote mechanism, prometheus-mcp + kubecost-mcp + security-mcp integrated.
- **Depth checkpoint (recommended addition):** for each agent completed in this phase, the non-owner teammate should be able to explain its failure modes and tool internals without reading the code, before moving to Phase 5. Any agent that fails this check gets flagged for simplification during Phase 6, not silently shipped shallow.

## Phase 5 — Dashboard (Weeks 13–14)
**Deliverable:** Next.js dashboard, real-time (or polling) logs, human-approval UI.
- Agent Overview, Decision Trail, Human-Approval Queue, Live Logs, Cost Simulation views built per Frontend Spec/Design Documents
- Secret redaction verified in logs view

## Phase 6 — Polish, Report, Viva Prep (Weeks 15–16)
**Deliverable:** all 3 demo scenarios run end-to-end live, recorded backup demo, written report, viva prep complete.
- Demo Scenarios A/B/C run successfully at least twice each before recording the fallback
- Fallback demo recorded and stored (`demo/recorded_backup/`)
- Report explicitly discloses: Cost Agent simulated pricing; Qdrant seed data provenance
- Security & Access demo-day checklist run (credential exposure check, log redaction check)
- Both team members rehearse explaining at least one full scenario path without notes

## Milestone Checkpoints (recommended, not in original doc)
- **End of Phase 2:** advisor sign-off that local-only/zero-cost scope is acceptable, if not already confirmed.
- **End of Phase 3:** conflict-resolution logic demoed to advisor/each other as a standalone proof — this is the piece most likely to be scrutinized, so validate it early rather than discovering issues in Phase 6.
- **End of Phase 4:** depth checkpoint results reviewed — decide if any agent needs simplifying before Phase 5/6 time is spent building UI around it.

## Risks Tracked
- 6 custom MCP servers is a large surface for 2 people even full-time — Phase 4 is the most likely phase to slip; build in slack rather than assuming exactly 3 weeks holds.
- Live-demo dependency on GitHub Actions + Trivy + local `kind` cluster all working simultaneously — mitigated by mandatory recorded fallback (Phase 6).
