"use client";

import { Check, X, Info, ShieldAlert } from "lucide-react";

export default function DecisionTrail({ state }: { state: any }) {
  if (!state || !state.agent_outputs) {
    return (
      <div style={{ color: "var(--text-muted)", fontSize: "13px", padding: "var(--spacing-4)" }}>
        No decision trail available. Start a run to see the event stream.
      </div>
    );
  }

  const agents = Object.entries(state.agent_outputs);
  const conflictFlag = state.conflict_flag;
  const finalDecision = state.final_decision;
  const ragContext = state.rag_context || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-6)", maxWidth: "840px" }}>
      {/* 1. Agent Votes */}
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-3)" }}>
        <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>1. Agent Evaluations</h3>
        {agents.map(([name, data]: any) => (
          <div key={name} style={{ display: "flex", alignItems: "flex-start", gap: "var(--spacing-3)", padding: "var(--spacing-3)", backgroundColor: "var(--bg-surface)", borderRadius: "8px", border: "1px solid var(--border)" }}>
            <div style={{ marginTop: "2px" }}>
              {data.vote === "proceed" ? <Check size={16} color="var(--status-healthy)" /> : <X size={16} color="var(--status-critical)" />}
            </div>
            <div>
              <div style={{ fontSize: "13px", fontWeight: 500 }}>{name}</div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>{data.reason}</div>
            </div>
          </div>
        ))}
      </div>

      {/* 2. Orchestrator Decision */}
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-3)" }}>
        <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>2. Orchestrator Conflict Resolution</h3>
        
        {conflictFlag ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-3)", padding: "var(--spacing-4)", backgroundColor: "var(--bg-surface)", borderRadius: "8px", border: "1px solid var(--border)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)", color: "var(--status-warning)" }}>
              <ShieldAlert size={16} />
              <span style={{ fontSize: "13px", fontWeight: 600 }}>CONFLICT DETECTED</span>
            </div>
            <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
              Agents submitted mixed votes. Querying Qdrant for historical precedents...
            </div>
            
            {/* RAG Precedents */}
            {ragContext.length > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--spacing-2)", marginTop: "var(--spacing-2)" }}>
                <div style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-primary)" }}>Retrieved Precedents:</div>
                {ragContext.map((hit: any, i: number) => (
                  <div key={i} style={{ padding: "var(--spacing-3)", backgroundColor: "var(--bg-primary)", borderRadius: "6px", border: "1px solid var(--border)", borderLeft: `3px solid ${i === 0 ? "var(--accent)" : "var(--border)"}` }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "var(--spacing-1)" }}>
                      <span className="mono" style={{ fontSize: "11px", color: "var(--text-secondary)" }}>Precedent {i+1}</span>
                      <span className="mono" style={{ fontSize: "11px", color: "var(--accent)", fontWeight: 600 }}>Score: {hit.score.toFixed(3)}</span>
                    </div>
                    <div style={{ fontSize: "12px", color: "var(--text-primary)" }}>{hit.document}</div>
                  </div>
                ))}
              </div>
            )}
            
            <div style={{ marginTop: "var(--spacing-2)", paddingTop: "var(--spacing-3)", borderTop: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "13px", fontWeight: 600 }}>Final Action:</span>
              <span style={{ 
                fontSize: "12px", fontWeight: 600, padding: "4px 8px", borderRadius: "4px", textTransform: "uppercase",
                backgroundColor: finalDecision === "proceed" ? "var(--status-healthy)" : finalDecision === "escalate" ? "var(--status-warning)" : "var(--status-critical)",
                color: "#000"
              }}>
                {finalDecision}
              </span>
            </div>
          </div>
        ) : finalDecision ? (
           <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-3)", padding: "var(--spacing-4)", backgroundColor: "var(--bg-surface)", borderRadius: "8px", border: "1px solid var(--border)" }}>
             <Info size={16} color="var(--status-healthy)" />
             <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Unanimous decision. No conflict resolution required. Action: <strong>PROCEED</strong></span>
           </div>
        ) : (
           <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-3)", padding: "var(--spacing-4)", backgroundColor: "var(--bg-surface)", borderRadius: "8px", border: "1px solid var(--border)" }}>
             <Info size={16} color="var(--text-secondary)" />
             <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>Waiting for all agents to cast their votes...</span>
           </div>
        )}
      </div>
    </div>
  );
}
