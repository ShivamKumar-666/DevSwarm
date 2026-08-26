"use client";

import { useState, useEffect } from "react";
import AgentOverview from "@/components/AgentOverview";
import DecisionTrail from "@/components/DecisionTrail";
import ApprovalQueue from "@/components/ApprovalQueue";
import CostSimulation from "@/components/CostSimulation";
import LiveLogs from "@/components/LiveLogs";
import { Play, LayoutDashboard, ActivitySquare, CheckSquare, Settings } from "lucide-react";

export default function Dashboard() {
  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<any>(null);
  const [queue, setQueue] = useState<any[]>([]);
  const [imageTag, setImageTag] = useState("nginx:1.14.2");

  const startRun = async () => {
    setRunStatus({ status: "running", logs: ["[System] Request initiated..."] });
    try {
      const res = await fetch("/api/swarm/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_tag: imageTag, deployment_name: "test-app" })
      });
      const data = await res.json();
      setRunId(data.run_id);
    } catch (e) {
      setRunStatus({ status: "failed", logs: ["[Error] Network request failed."] });
    }
  };

  const handleApprove = async (id: string, decision: string) => {
    try {
      const res = await fetch("/api/swarm/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: id, decision })
      });
      const data = await res.json();
      if (data.status === "error") {
        alert(`Approval failed: ${data.message}`);
        return false;
      }
      return true;
    } catch (e) {
      alert("Could not reach backend. Is the server running?");
      return false;
    } finally {
      fetchData(); // Immediately refresh
    }
  };

  const fetchData = async () => {
    if (runId) {
      const statusRes = await fetch(`/api/swarm/status/${runId}`);
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setRunStatus(statusData);
      }
    }
    const queueRes = await fetch(`/api/swarm/queue`);
    if (queueRes.ok) {
      const queueData = await queueRes.json();
      setQueue(queueData.queue);
    }
  };

  useEffect(() => {
    // Fetch immediately on mount, then every 2s
    fetchData();
    const interval = setInterval(() => {
      fetchData();
    }, 2000);
    return () => clearInterval(interval);
  }, [runId]);

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Sidebar */}
      <aside style={{ width: "240px", backgroundColor: "var(--bg-surface)", borderRight: "1px solid var(--border)", display: "flex", flexDirection: "column" }}>
        <div style={{ padding: "var(--spacing-6)", borderBottom: "1px solid var(--border)" }}>
          <h1 style={{ fontSize: "16px", fontWeight: 700, letterSpacing: "-0.5px", margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
            <ActivitySquare size={20} color="var(--accent)" />
            DevSwarm
          </h1>
        </div>
        <nav style={{ padding: "var(--spacing-4)", display: "flex", flexDirection: "column", gap: "var(--spacing-2)" }}>
          <a href="#" style={{ display: "flex", alignItems: "center", gap: "12px", padding: "8px 12px", borderRadius: "6px", backgroundColor: "var(--bg-surface-raised)", color: "var(--text-primary)", textDecoration: "none", fontSize: "13px", fontWeight: 500 }}>
            <LayoutDashboard size={16} /> Overview
          </a>
          <a href="#approvals" style={{ display: "flex", alignItems: "center", gap: "12px", padding: "8px 12px", borderRadius: "6px", color: "var(--text-secondary)", textDecoration: "none", fontSize: "13px", fontWeight: 500 }}>
            <CheckSquare size={16} /> Approvals
            {queue.length > 0 && (
              <span style={{ marginLeft: "auto", backgroundColor: "var(--status-warning)", color: "#000", fontSize: "10px", padding: "2px 6px", borderRadius: "99px", fontWeight: 700 }}>
                {queue.length}
              </span>
            )}
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, padding: "var(--spacing-8)", display: "flex", flexDirection: "column", gap: "var(--spacing-8)" }}>
        
        {/* Header Controls */}
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h2 style={{ fontSize: "20px", fontWeight: 600, margin: "0 0 4px 0" }}>Swarm Orchestration</h2>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: 0 }}>Monitor multi-agent execution and RAG-based conflict resolution.</p>
          </div>
          
          <div style={{ display: "flex", gap: "var(--spacing-3)", alignItems: "center" }}>
            <input 
              value={imageTag}
              onChange={e => setImageTag(e.target.value)}
              className="mono"
              style={{ padding: "8px 12px", borderRadius: "6px", border: "1px solid var(--border)", backgroundColor: "var(--bg-surface)", color: "var(--text-primary)", fontSize: "13px", width: "160px" }}
              placeholder="Image tag"
            />
            <button 
              onClick={startRun}
              disabled={runStatus?.status === "running"}
              style={{
                backgroundColor: "var(--text-primary)", color: "var(--bg-primary)",
                border: "none", borderRadius: "6px", padding: "8px 16px",
                fontSize: "13px", fontWeight: 600, cursor: "pointer",
                display: "flex", alignItems: "center", gap: "8px",
                opacity: runStatus?.status === "running" ? 0.7 : 1
              }}
            >
              <Play size={14} fill="currentColor" /> {runStatus?.status === "running" ? "Running..." : "Trigger Swarm"}
            </button>
          </div>
        </header>

        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "var(--spacing-6)", alignItems: "start" }}>
          
          {/* Left Column */}
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-8)" }}>
            <section>
              <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "var(--spacing-4)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Agent Status</h3>
              <AgentOverview state={runStatus?.state || {}} />
            </section>
            
            <section>
              <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "var(--spacing-4)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Decision Trail</h3>
              <DecisionTrail state={runStatus?.state || {}} />
            </section>

            <section id="approvals">
              <h3 style={{ fontSize: "14px", fontWeight: 600, color: queue.length > 0 ? "var(--status-warning)" : "var(--text-secondary)", marginBottom: "var(--spacing-4)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Requires Approval {queue.length > 0 ? `(${queue.length})` : ""}</h3>
              {queue.length > 0 ? (
                <ApprovalQueue queue={queue} onApprove={handleApprove} />
              ) : (
                <div style={{ padding: "24px", border: "1px dashed var(--border)", borderRadius: "8px", textAlign: "center", color: "var(--text-secondary)", fontSize: "13px" }}>
                  No pending approvals. Trigger a swarm run to see escalations here.
                </div>
              )}
            </section>
            
            <section>
              <CostSimulation state={runStatus?.state || {}} />
            </section>
          </div>

          {/* Right Column */}
          <div style={{ position: "sticky", top: "var(--spacing-8)" }}>
             <LiveLogs logs={runStatus?.logs || []} />
          </div>

        </div>
      </main>
    </div>
  );
}
