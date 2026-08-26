# DevSwarm 🐝

DevSwarm is an autonomous, multi-agent orchestrator built with LangGraph and FastAPI that uses Retrieval-Augmented Generation (RAG) to autonomously resolve CI/CD pipeline conflicts.

By breaking away from traditional rigid rule-engines, DevSwarm introduces a dynamic, context-aware decision-making process for complex deployment conflicts (e.g., balancing high-severity security vulnerabilities against critical incident rollbacks and budget constraints).

---

## 🏗️ Architecture & Core Components

DevSwarm consists of three main architectural layers:

1. **The Agents (LangChain)**
   - **Deploy Agent:** Manages deployments to Kubernetes via the `k8s-mcp` server.
   - **Security Agent:** Scans Docker images for vulnerabilities using the `security-mcp` (Trivy).
   - **Monitor Agent:** Checks system load via Prometheus (`prometheus-mcp`).
   - **Cost Agent:** Simulates cloud pricing constraints via Kubecost (`kubecost-mcp`).
   - **Incident Agent:** Monitors for system spikes or historical anomalies to initiate rollbacks.

2. **Model Context Protocol (MCP)**
   Each agent accesses external tools strictly through isolated MCP servers. This ensures agents are completely decoupled from external tooling, allowing tool-swapping without modifying agent logic.

3. **Orchestrator & RAG Resolution (The Novelty Claim)**
   When agents submit conflicting votes (e.g. Deploy wants to `PROCEED`, but Security wants to `BLOCK`), the LangGraph Orchestrator halts the pipeline. It then embeds the conflict state and queries a **Qdrant Vector Database** containing historical deployment precedents. 
   - If a precedent matches the current conflict with a **High Confidence Score (>= 0.80)**, the system **autonomously resolves** the conflict based on past actions.
   - If the confidence is low, the pipeline is escalated to the **Human Approval Dashboard**.
   - Upon human intervention, the final decision is saved back into Redis and Qdrant, closing the learning loop.

---

## 💻 Tech Stack

- **Backend:** Python, FastAPI, LangGraph, LangChain, Groq API (Llama3)
- **Frontend:** Next.js, React, TailwindCSS
- **State Management:** Redis Stack (RedisJSON / RediSearch)
- **Vector Database:** Qdrant (FastEmbed / BAAI-bge-small-en)
- **Tooling:** Model Context Protocol (MCP), Docker, Kubernetes (Kind), Trivy, Prometheus

---

## 🚀 Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Node.js (v18+)
- Python (3.11+)
- Groq API Key

### 1. Start External Infrastructure (Redis & Qdrant)
```bash
docker-compose up -d
```

### 2. Install & Start the Backend
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -r requirements.txt

# Seed the Qdrant database with historical precedents
python scripts/seed_qdrant.py --reset

# Start the FastAPI Server
export GROQ_API_KEY="your-groq-api-key"
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

### 3. Install & Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

The DevSwarm Dashboard will be accessible at `http://localhost:3000`.

---

## 🎬 Demo Scenarios

DevSwarm can be tested via three distinct scenarios designed for the final presentation. You can trigger these via the provided `simulate_ci.ps1` script or directly through the Dashboard UI.

1. **Scenario A: Clean Deployment**
   - **Action:** Triggers a deployment for `nginx:latest`.
   - **Result:** All agents unanimously vote to `PROCEED`. The pipeline passes without conflict.

2. **Scenario B: Autonomous Resolution (High Confidence Match)**
   - **Action:** Triggers a deployment for `nginx:1.14.2`.
   - **Result:** Agents submit mixed votes (Deploy/Proceed, Security/Block, Monitor/Monitor, Cost/Block, Incident/Rollback).
   - The Orchestrator queries Qdrant, finds an exact historical match in `past_incidents` (confidence >= 0.80), and autonomously enforces a `ROLLBACK` without requiring human intervention.

3. **Scenario C: Human Escalation (Low Confidence)**
   - **Action:** Triggers a custom or untested image tag.
   - **Result:** Agents submit mixed votes. Qdrant is queried but cannot find a precedent above the confidence threshold (e.g. score ~0.74).
   - The pipeline halts, and the state is pushed to the **Requires Approval** queue on the Next.js Dashboard.
   - The human clicks "Proceed" or "Rollback". The decision is executed, and a new precedent is learned and saved back to Qdrant dynamically.

---

## 📝 Academic Disclosure
- **Pricing:** The `kubecost-mcp` Cost Agent relies on simulated, mocked pricing data for the purpose of this demonstration.
- **Precedents:** Initial data in the Qdrant vector database (`past_incidents`, `past_security_scans`, `cost_history`, `past_deployments`) contains synthetic scenarios crafted to validate the RAG resolution engine.
