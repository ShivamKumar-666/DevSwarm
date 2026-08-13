from qdrant_client import QdrantClient

def seed():
    print("Connecting to Qdrant...")
    client = QdrantClient(url="http://localhost:6333")

    collections = [
        "past_deployments",
        "past_incidents",
        "past_security_scans",
        "cost_history"
    ]

    existing_collections = [c.name for c in client.get_collections().collections]

    for col in collections:
        if col in existing_collections:
            print(f"Collection '{col}' already exists. Recreating...")
            client.delete_collection(col)

        print(f"Setting up collection '{col}' for fastembed...")
        client.set_model("BAAI/bge-small-en-v1.5")
        
        # fastembed native integration allows us to just add docs
        client.create_collection(
            collection_name=col,
            vectors_config=client.get_fastembed_vector_params()
        )

    # 1. Past Deployments
    print("Seeding past_deployments...")
    client.add(
        collection_name="past_deployments",
        documents=[
            "Deployment to staging failed due to missing secrets.",
            "Deployment to production successful. High test coverage.",
            "Deployment blocked. Branch protection rules violated (force push detected)."
        ],
        metadata=[
            {"status": "failed", "reason": "missing secrets"},
            {"status": "success", "reason": "high test coverage"},
            {"status": "blocked", "reason": "branch protection"}
        ]
    )

    # 2. Past Security Scans
    print("Seeding past_security_scans...")
    client.add(
        collection_name="past_security_scans",
        documents=[
            "Critical vulnerability CVE-2023-111 found in dependency. Deployment blocked.",
            "Medium severity CVE-2023-222 found in non-exposed internal tool. Deployment allowed.",
            "No vulnerabilities found. Clean scan."
        ],
        metadata=[
            {"decision": "escalate", "severity": "critical", "cve": "CVE-2023-111"},
            {"decision": "proceed", "severity": "medium", "cve": "CVE-2023-222"},
            {"decision": "proceed", "severity": "none"}
        ]
    )

    # 3. Past Incidents
    print("Seeding past_incidents...")
    client.add(
        collection_name="past_incidents",
        documents=[
            "High memory usage detected on auth service. Rollback initiated.",
            "CPU spike during batch processing window. Monitored but no action taken.",
            "Database connection timeout. Restarted pods."
        ],
        metadata=[
            {"action": "rollback", "trigger": "memory"},
            {"action": "ignore", "trigger": "cpu_spike"},
            {"action": "restart", "trigger": "db_timeout"}
        ]
    )

    # 4. Cost History
    print("Seeding cost_history...")
    client.add(
        collection_name="cost_history",
        documents=[
            "Kubernetes cluster cost increased by 200% due to unoptimized queries.",
            "Cost reduced by 30% after resizing node pools.",
            "Standard operational cost maintained within budget."
        ],
        metadata=[
            {"action": "alert", "trend": "up"},
            {"action": "monitor", "trend": "down"},
            {"action": "monitor", "trend": "stable"}
        ]
    )

if __name__ == "__main__":
    seed()
    print("Seeding complete!")
