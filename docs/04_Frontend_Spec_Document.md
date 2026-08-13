# DevSwarm — Frontend Spec Document

## 1. Purpose
Functional specification for the Next.js SRE Dashboard — the primary interface a viewer (grader, teammate, or on-call user) uses to observe and interact with the DevSwarm swarm.

## 2. Stack
- Next.js (App Router) + React
- Recharts (charts: anomaly trends, cost simulation)
- WebSocket (or polling fallback) to the Orchestrator's FastAPI backend for live updates
- No external CSS framework dependency required beyond what's already used in AidFlow's frontend, for stack consistency — confirm with teammate before deciding.

## 3. Core Views

### 3.1 Agent Status Overview (home view)
- Card per agent (Deploy, Monitor, Security, Cost, Incident) showing: current status (idle/running/blocked), last run timestamp, last output summary.
- Cost Agent card must carry a persistent "Simulated pricing" label — not just in a tooltip.

### 3.2 Decision Trail / Timeline
- Chronological feed of events → agent outputs → Orchestrator decisions.
- Each Orchestrator decision entry expands to show: retrieved precedent(s) from Qdrant (which past incident/deployment it matched), computed confidence score, and final decision (proceed/block/escalate).
- This view is the one most likely to be walked through live in the viva — prioritize clarity over visual density.

### 3.3 Human-Approval UI
- Queue of `escalate`d decisions awaiting human input.
- Each item shows: what triggered it, the conflicting agent outputs, the retrieved precedent and why it wasn't confident enough, and Approve / Reject / Modify actions.
- Action taken here must be logged back into Qdrant as a new precedent record (closes the learning loop).

### 3.4 Live Logs
- Streaming logs per agent run (WebSocket), scoped/filterable by agent and by demo scenario.
- Secrets/tokens must be redacted before reaching this view (see Security & Access Document §7).

### 3.5 Cost Simulation View
- Right-sizing suggestions from Cost Agent, charted (Recharts).
- Explicit, unmissable "Simulated — not live billing data" banner at the top of this view specifically, not just a footnote.

## 4. Non-Functional Requirements
- Must run entirely via `docker-compose up` alongside the rest of the stack — no separate manual frontend setup for the demo.
- Must gracefully handle a backend/agent being down (don't crash the whole dashboard if one MCP server is unreachable) — this matters directly for demo-day resilience.
- Reasonable load time on a laptop during a live demo — avoid heavy client-side bundles if avoidable.

## 5. Explicitly Out of Scope (v1)
- User authentication/multi-user roles — single local demo user is sufficient for an academic project.
- Mobile responsive layout — desktop-only for the demo.
- Historical analytics beyond what's needed for the report's evaluation metrics (MTTR, false-positive rate, conflict rate) — those can be computed from logs directly for the report rather than built as a dashboard feature.

## 6. Open Items
- Confirm polling vs. WebSocket — WebSocket is more impressive but adds failure surface for a live demo; polling is more failure-tolerant. Recommend deciding based on how much frontend time is available given the 2-person team.
- Confirm whether the dashboard needs to support all 3 demo scenarios simultaneously visible, or can be scenario-scoped/reset between demo runs.
