# DevSwarm — Security & Access Document

## 1. Purpose
Defines the security posture, credential handling, and access boundaries for DevSwarm — both the security *feature* (the Security Agent) and the security *of the system itself* (how DevSwarm protects its own credentials, infra, and blast radius).

## 2. Threat Model (Scoped)
DevSwarm is a local, zero-cost academic project, not a production system. The relevant threats are:
- Leaked credentials (GitHub tokens, LLM API keys) committed to the repo.
- An agent taking a destructive action (e.g. bad rollback, wrong `kubectl` command) against the `kind` cluster.
- A prompt-injected or malformed LLM response causing an MCP tool call with unintended parameters.
- Demo-time exposure of secrets on screen during a live viva.

Out of scope: multi-tenant isolation, external attacker threat modeling, production-grade RBAC — not applicable to a single local `kind` cluster with no public exposure.

## 3. Credential & Secrets Management
- All secrets (GitHub token, Groq/Gemini API key, MCP server auth if any) live in a `.env` file, never committed.
- `.gitignore` must cover `.env`, any `*.pem`/`*.key` files, and local Qdrant/Postgres data volumes.
- Use a secret-scanning pre-commit hook (e.g. `gitleaks`) or a documented manual check before every push — repos have shipped leaked keys before; verify none exist prior to submission/demo.
- GitHub token scoped to the minimum permissions needed (repo + workflow trigger), not a full-access personal token.

## 4. Agent Action Boundaries
- **Deploy Agent:** may apply manifests and roll back only within the local `kind` cluster's dedicated namespace — never cluster-wide or against kube-system.
- **Incident Agent:** auto-remediation actions (pod restart, rollback) must be limited to a pre-approved action list; anything outside that list routes to human approval via the dashboard, regardless of confidence score.
- **Security Agent:** can block a deploy (deny-by-default on unresolved high/critical CVEs) but cannot itself merge or force a deploy — asymmetric permission by design.
- **Cost Agent:** read-only / suggestion-only — never executes right-sizing actions automatically, since its pricing data is simulated.

## 5. Orchestrator Escalation Policy
- Confidence score below the defined threshold (document the exact number/method used) → `escalate`, never auto-proceed.
- All escalations require explicit human approval via the dashboard before any state-changing MCP tool call executes.
- Every Orchestrator decision (proceed/block/escalate), including the retrieved precedent and confidence score, is logged immutably (Qdrant + Postgres/log store) for audit and for the report's evaluation metrics.

## 6. Security Agent — Tooling Detail
- **Trivy:** image/repo CVE scanning; block on unresolved high/critical severity by default (document the exact severity threshold used).
- **OWASP ZAP (local):** dynamic scanning where applicable to the demo app.
- Report and viva must be able to explain: what happens when Trivy and ZAP disagree, and what "block" actually does mechanically (fails the PR check / halts the pipeline — specify which).

## 7. Data Handling
- Qdrant seed data (incident/deployment/security/cost records): if using any real historical data (e.g. from AidFlow/BidFlow logs), strip any credentials, internal URLs, or personal data before ingesting. If synthetic, label it as such in the collection metadata itself, not only in the report.
- Dashboard human-approval UI should not display raw secrets or tokens in logs shown on screen — redact before rendering, since this UI will be on screen during the live demo.

## 8. Demo-Day Checklist
- Confirm `.env` is not visible in any terminal window that will be shared on screen.
- Confirm dashboard log views redact secrets/tokens.
- Confirm the fallback recorded demo also doesn't expose secrets (re-check if it was recorded before a rotation).
- Rotate any credentials that were ever exposed during development, even briefly, before final submission.

## 9. Open Items
- Exact CVE severity threshold for auto-block (Security Agent) — to be decided and documented.
- Exact confidence-score threshold for Orchestrator escalation — to be decided and documented, ideally justified in the report rather than picked arbitrarily.
- Final decision on real vs. synthetic Qdrant seed data (data handling implications differ — see §7).
