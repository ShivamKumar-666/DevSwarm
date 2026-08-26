"use client";

import { useState } from "react";
import { Check, X, ShieldAlert, CheckCircle2 } from "lucide-react";

export default function ApprovalQueue({ queue, onApprove }: { queue: any[], onApprove: (id: string, decision: string) => void }) {
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [decisions, setDecisions] = useState<Record<string, { decision: string; timestamp: string }>>({});

  const handleAction = async (id: string, decision: string) => {
    setLoadingId(id);
    try {
      await onApprove(id, decision);
      // Record the decision locally so we can show confirmation even after it leaves the queue
      setDecisions(prev => ({
        ...prev,
        [id]: { decision, timestamp: new Date().toLocaleTimeString() }
      }));
    } finally {
      setLoadingId(null);
    }
  };

  // Show recent decisions as confirmations (even if item left the queue)
  const recentDecisions = Object.entries(decisions);

  if (!queue || queue.length === 0) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {recentDecisions.map(([id, { decision, timestamp }]) => (
          <div key={id} style={{
            display: "flex", alignItems: "center", gap: "12px",
            padding: "14px 16px", borderRadius: "8px",
            backgroundColor: "color-mix(in srgb, var(--status-success, #22c55e) 10%, transparent)",
            border: "1px solid var(--status-success, #22c55e)"
          }}>
            <CheckCircle2 size={18} color="var(--status-success, #22c55e)" />
            <div>
              <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
                Decision recorded at {timestamp}
              </div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px" }}>
                Run <span style={{ fontFamily: "monospace" }}>{id.substring(0, 8)}</span> → Human chose: <strong style={{ textTransform: "uppercase" }}>{decision}</strong>. Precedent saved to Qdrant.
              </div>
            </div>
          </div>
        ))}
        {recentDecisions.length === 0 && (
          <div style={{ padding: "24px", border: "1px dashed var(--border)", borderRadius: "8px", textAlign: "center", color: "var(--text-secondary)", fontSize: "13px" }}>
            No pending approvals. Trigger a swarm run to see escalations here.
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-4)", maxWidth: "840px" }}>
      {/* Show any already-processed decisions above */}
      {recentDecisions.map(([id, { decision, timestamp }]) => (
        <div key={id} style={{
          display: "flex", alignItems: "center", gap: "12px",
          padding: "14px 16px", borderRadius: "8px",
          backgroundColor: "color-mix(in srgb, var(--status-success, #22c55e) 10%, transparent)",
          border: "1px solid var(--status-success, #22c55e)"
        }}>
          <CheckCircle2 size={18} color="var(--status-success, #22c55e)" />
          <div>
            <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
              Decision recorded at {timestamp}
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px" }}>
              Run <span style={{ fontFamily: "monospace" }}>{id.substring(0, 8)}</span> → Human chose: <strong style={{ textTransform: "uppercase" }}>{decision}</strong>. Precedent saved to Qdrant.
            </div>
          </div>
        </div>
      ))}

      {/* Pending items */}
      {queue.map(item => {
        const state = item.state;
        const agentOutputs = state?.agent_outputs || {};
        const votes = Object.entries(agentOutputs).map(([agent, output]: [string, any]) => ({
          agent,
          vote: output?.vote || "unknown",
          reason: output?.reason || ""
        }));
        const ragContext = state?.rag_context || [];

        return (
          <div key={item.run_id} style={{ backgroundColor: "var(--bg-surface)", borderRadius: "8px", border: "1px solid var(--status-warning)", overflow: "hidden" }}>
            <div style={{ padding: "var(--spacing-4)", backgroundColor: "color-mix(in srgb, var(--status-warning) 10%, transparent)", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: "var(--spacing-3)" }}>
              <ShieldAlert size={18} color="var(--status-warning)" />
              <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>
                Escalated Decision for run: <span className="mono">{item.run_id.substring(0,8)}</span>
              </div>
            </div>

            <div style={{ padding: "var(--spacing-4)" }}>
              <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "var(--spacing-4)" }}>
                The orchestrator detected a conflict but could not find a high-confidence Qdrant precedent to automatically resolve it. Human approval required.
              </div>

              {/* Agent Votes */}
              {votes.length > 0 && (
                <div style={{ marginBottom: "var(--spacing-4)" }}>
                  <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>Agent Votes</div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    {votes.map(({ agent, vote, reason }) => (
                      <div key={agent} style={{ display: "flex", alignItems: "flex-start", gap: "10px", fontSize: "12px" }}>
                        <span style={{
                          padding: "2px 8px", borderRadius: "99px", fontWeight: 700, fontSize: "10px",
                          backgroundColor: vote === "proceed" ? "color-mix(in srgb, #22c55e 20%, transparent)" : "color-mix(in srgb, #ef4444 20%, transparent)",
                          color: vote === "proceed" ? "#22c55e" : "#ef4444",
                          minWidth: "52px", textAlign: "center", textTransform: "uppercase"
                        }}>{vote}</span>
                        <span style={{ fontWeight: 600, color: "var(--text-primary)", minWidth: "80px" }}>{agent}</span>
                        <span style={{ color: "var(--text-secondary)", flex: 1 }}>{reason.slice(0, 120)}{reason.length > 120 ? "…" : ""}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Qdrant Precedents */}
              {ragContext.length > 0 && (
                <div style={{ marginBottom: "var(--spacing-4)" }}>
                  <div style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "8px" }}>Qdrant Precedents (all below 0.85 threshold)</div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    {ragContext.map((p: any, i: number) => (
                      <div key={i} style={{ display: "flex", gap: "10px", fontSize: "12px", alignItems: "center" }}>
                        <span style={{ fontFamily: "monospace", color: "var(--status-warning)", minWidth: "48px" }}>{p.score?.toFixed(3)}</span>
                        <span style={{ color: "var(--text-secondary)" }}>{p.document}</span>
                        <span style={{ marginLeft: "auto", fontSize: "10px", padding: "1px 6px", borderRadius: "4px", backgroundColor: "var(--bg-surface-raised)", color: "var(--text-secondary)" }}>{p.metadata?.decision}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ display: "flex", gap: "var(--spacing-3)", marginTop: "var(--spacing-6)" }}>
                <button
                  onClick={() => handleAction(item.run_id, "proceed")}
                  disabled={loadingId === item.run_id}
                  style={{
                    backgroundColor: "var(--text-primary)", color: "var(--bg-primary)",
                    border: "none", borderRadius: "6px", padding: "8px 16px",
                    fontSize: "13px", fontWeight: 600, cursor: "pointer",
                    display: "flex", alignItems: "center", gap: "8px",
                    opacity: loadingId === item.run_id ? 0.7 : 1
                  }}
                >
                  <Check size={16} /> {loadingId === item.run_id ? "Processing…" : "Approve & Proceed"}
                </button>
                <button
                  onClick={() => handleAction(item.run_id, "block")}
                  disabled={loadingId === item.run_id}
                  style={{
                    backgroundColor: "transparent", color: "var(--status-critical)",
                    border: "1px solid var(--status-critical)", borderRadius: "6px",
                    padding: "8px 16px", fontSize: "13px", fontWeight: 600,
                    cursor: "pointer", display: "flex", alignItems: "center", gap: "8px",
                    opacity: loadingId === item.run_id ? 0.7 : 1
                  }}
                >
                  <X size={16} /> Reject & Block
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
