"use client";

import { CheckCircle2, AlertTriangle, XCircle, Shield, Activity, DollarSign, ArrowUpRight, Zap } from "lucide-react";

type AgentStatus = "healthy" | "warning" | "critical" | "simulated" | "idle";

interface Agent {
  id: string;
  name: string;
  icon: any;
  status: AgentStatus;
  lastRun: string;
  summary: string;
}

const getStatusColor = (status: AgentStatus) => {
  switch (status) {
    case "healthy": return "var(--status-healthy)";
    case "warning": return "var(--status-warning)";
    case "critical": return "var(--status-critical)";
    case "simulated": return "var(--status-simulated)";
    default: return "var(--text-secondary)";
  }
};

const getStatusIcon = (status: AgentStatus) => {
  switch (status) {
    case "healthy": return <CheckCircle2 size={14} color="var(--status-healthy)" />;
    case "warning": return <AlertTriangle size={14} color="var(--status-warning)" />;
    case "critical": return <XCircle size={14} color="var(--status-critical)" />;
    default: return null;
  }
};

export default function AgentOverview({ state }: { state: any }) {
  // Derive agent states from LangGraph state if available, otherwise mock
  const agents: Agent[] = [
    {
      id: "deploy",
      name: "Deploy Agent",
      icon: ArrowUpRight,
      status: state?.agent_outputs?.deploy ? (state.agent_outputs.deploy.vote === "proceed" ? "healthy" : "warning") : "idle",
      lastRun: new Date().toLocaleTimeString(),
      summary: state?.agent_outputs?.deploy?.reason || "Waiting for run...",
    },
    {
      id: "monitor",
      name: "Monitor Agent",
      icon: Activity,
      status: state?.agent_outputs?.monitor ? "healthy" : "idle",
      lastRun: new Date().toLocaleTimeString(),
      summary: state?.agent_outputs?.monitor?.reason || "Waiting for run...",
    },
    {
      id: "security",
      name: "Security Agent",
      icon: Shield,
      status: state?.agent_outputs?.security?.vote === "block" ? "critical" : state?.agent_outputs?.security ? "healthy" : "idle",
      lastRun: new Date().toLocaleTimeString(),
      summary: state?.agent_outputs?.security?.reason || "Waiting for run...",
    },
    {
      id: "cost",
      name: "Cost Agent",
      icon: DollarSign,
      status: state?.agent_outputs?.cost?.vote === "block" ? "warning" : state?.agent_outputs?.cost ? "simulated" : "idle",
      lastRun: new Date().toLocaleTimeString(),
      summary: state?.agent_outputs?.cost?.reason || "Waiting for run...",
    },
    {
      id: "incident",
      name: "Incident Agent",
      icon: Zap,
      status: state?.agent_outputs?.incident?.vote === "rollback" ? "critical" : state?.agent_outputs?.incident ? "healthy" : "idle",
      lastRun: new Date().toLocaleTimeString(),
      summary: state?.agent_outputs?.incident?.reason || "Waiting for run...",
    }
  ];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "var(--spacing-4)" }}>
      {agents.map(agent => (
        <div key={agent.id} style={{
          backgroundColor: "var(--bg-surface)",
          border: `1px solid ${agent.status === "simulated" ? "var(--status-simulated)" : "var(--border)"}`,
          borderStyle: agent.status === "simulated" ? "dashed" : "solid",
          borderRadius: "8px",
          padding: "var(--spacing-4)",
          transition: "background-color 0.2s"
        }}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "var(--bg-surface-raised)"}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "var(--bg-surface)"}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--spacing-3)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--spacing-2)" }}>
              <agent.icon size={16} color="var(--text-secondary)" />
              <span style={{ fontSize: "14px", fontWeight: 600 }}>{agent.name}</span>
            </div>
            
            <div style={{
              display: "flex", alignItems: "center", gap: "4px",
              padding: "2px 8px", borderRadius: "999px",
              backgroundColor: `color-mix(in srgb, ${getStatusColor(agent.status)} 15%, transparent)`,
              color: getStatusColor(agent.status),
              fontSize: "11px", fontWeight: 500, textTransform: "uppercase"
            }}>
              {getStatusIcon(agent.status)}
              {agent.status}
            </div>
          </div>
          
          <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "var(--spacing-4)", height: "40px", overflow: "hidden", textOverflow: "ellipsis" }}>
            {agent.summary}
          </div>
          
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "11px", color: "var(--text-secondary)", borderTop: "1px solid var(--border)", paddingTop: "var(--spacing-2)" }}>
            <span className="mono" suppressHydrationWarning>{agent.lastRun}</span>
            {agent.status === "simulated" && <span style={{ color: "var(--status-simulated)" }}>Simulated Data</span>}
          </div>
        </div>
      ))}
    </div>
  );
}
