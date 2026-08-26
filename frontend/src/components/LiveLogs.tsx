"use client";

import { useEffect, useRef } from "react";
import { Terminal } from "lucide-react";

export default function LiveLogs({ logs }: { logs: string[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  // Redact secrets like API keys or UUIDs just in case they leak in logs
  const redact = (text: string) => {
    return text.replace(/gsk_[a-zA-Z0-9]{40,}/g, "gsk_***REDACTED***")
               .replace(/sk-[a-zA-Z0-9]{40,}/g, "sk-***REDACTED***");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", backgroundColor: "#000", borderRadius: "8px", border: "1px solid var(--border)", height: "400px", overflow: "hidden" }}>
      <div style={{ padding: "10px 16px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: "var(--spacing-2)", backgroundColor: "var(--bg-surface)" }}>
        <Terminal size={14} color="var(--text-secondary)" />
        <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px" }}>Live Swarm Logs</span>
      </div>
      <div ref={scrollRef} style={{ flex: 1, overflowY: "auto", padding: "16px", display: "flex", flexDirection: "column", gap: "6px" }}>
        {logs.length === 0 ? (
          <div style={{ color: "var(--text-muted)", fontSize: "12px", fontFamily: "var(--font-jetbrains-mono)" }}>
            Waiting for swarm execution to begin...
          </div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="mono" style={{ fontSize: "12px", color: log.includes("[Error]") ? "var(--status-critical)" : log.includes("[System]") ? "var(--accent)" : "var(--text-primary)", lineHeight: 1.4 }}>
              {redact(log)}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
