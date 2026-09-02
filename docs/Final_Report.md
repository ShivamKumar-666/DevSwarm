# DevSwarm: Autonomous CI/CD Conflict Resolution via Retrieval-Augmented Generation

## 1. Executive Summary
DevSwarm is an autonomous, multi-agent continuous integration and continuous deployment (CI/CD) orchestrator. Unlike traditional CI/CD pipelines that rely on rigid, hardcoded rule engines, DevSwarm introduces a dynamic, context-aware decision-making process. By utilizing LangGraph, FastAPI, and Retrieval-Augmented Generation (RAG), the system intelligently resolves complex deployment conflicts—such as balancing high-severity security vulnerabilities against critical incident rollbacks and budget constraints—without requiring immediate human intervention.

## 2. Project Motivation & Novelty Claim
Modern deployment pipelines often pause or fail when automated checks produce conflicting results (e.g., a critical hotfix must be deployed immediately, but the security scanner blocks it due to an unpatched vulnerability). Traditionally, this requires an engineer to manually review and override the pipeline.

**Novelty Claim:** DevSwarm replaces manual overrides with a **Retrieval-Augmented Generation (RAG) Conflict Resolution Engine**. When agents submit conflicting votes, the orchestrator queries a vector database containing historical deployment precedents. If a high-confidence match is found based on past organizational decisions, DevSwarm autonomously resolves the conflict. This closes the learning loop, allowing the CI/CD pipeline to learn from past human interventions.

## 3. System Architecture
DevSwarm is built on a decoupled, three-tier architecture:

### 3.1 The Multi-Agent System (LangChain/LangGraph)
Five distinct AI agents operate in parallel to evaluate incoming deployment payloads:
*   **Deploy Agent:** Evaluates Kubernetes deployment health and rollout status via the `k8s-mcp` server.
*   **Security Agent:** Scans container images for vulnerabilities (CVEs) using the `security-mcp` (Trivy).
*   **Monitor Agent:** Analyzes system load and CPU constraints via the `prometheus-mcp` server.
*   **Cost Agent:** Evaluates cloud pricing and budget constraints via the `kubecost-mcp` server.
*   **Incident Agent:** Monitors for system spikes or anomalies to initiate emergency rollbacks.

### 3.2 Model Context Protocol (MCP) Integration
To ensure the AI agents remain entirely decoupled from the underlying infrastructure, all external tool access is facilitated through Model Context Protocol (MCP) servers. This allows underlying tools (e.g., switching from Trivy to Snyk) to be hot-swapped without modifying the core agent logic.

### 3.3 The RAG Orchestrator (Qdrant & Redis)
*   **State Management:** Redis Stack (RedisJSON) maintains the state of the swarm run, agent outputs, and final decisions.
*   **Vector Database:** Qdrant stores historical deployment precedents using `BAAI-bge-small-en` embeddings.
*   **Conflict Resolution:** If the aggregate vote results in a conflict, the state is embedded and queried against Qdrant. A confidence threshold (>= 0.80) determines if the AI can autonomously enforce a decision or if it must escalate to a human engineer. *(Note: The 0.80 threshold is currently a tuned hyperparameter based on heuristic testing during development, rather than a rigorously validated ML baseline).*

## 4. Academic Disclosures
In accordance with project requirements, the following simulated data sources are explicitly disclosed:

1.  **Simulated Pricing Data (Cost Agent):** The `kubecost-mcp` server utilizes simulated, mocked pricing data to demonstrate budget-constraint logic. It is not connected to a live AWS/GCP billing API to prevent accidental cloud charges during development and demonstration.
2.  **Synthetic Seed Data Provenance (Qdrant):** The initial historical precedents seeded into the Qdrant vector database (including `past_incidents`, `past_security_scans`, `cost_history`, and `past_deployments`) are synthetic scenarios. These scenarios were specifically crafted by the development team to validate the retrieval accuracy and confidence scoring of the RAG resolution engine.

## 5. Conclusion
DevSwarm successfully demonstrates that CI/CD pipelines can transition from static rule execution to dynamic, learned behavior. By integrating MCP for tool abstraction and RAG for precedent-based decision-making, DevSwarm reduces pipeline bottlenecks, minimizes pager fatigue for Site Reliability Engineers (SREs), and safely automates complex deployment resolutions.
