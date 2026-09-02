"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function CostSimulation({ state }: { state: any }) {
  if (!state || !state.agent_outputs || !state.agent_outputs.cost) {
    return (
      <div style={{ color: "var(--text-muted)", fontSize: "13px", padding: "var(--spacing-4)", border: "1px dashed var(--status-simulated)", borderRadius: "8px" }}>
        No cost simulation data available yet.
      </div>
    );
  }

  const costData = state.agent_outputs.cost;
  const costResult = costData.cost_result || {};
  const breakdown = costResult.breakdown || { "cpu_cost": 60.0, "memory_cost": 20.0 };
  
  const chartData = Object.entries(breakdown).map(([key, value]) => ({
    name: key.replace("_cost", "").toUpperCase(),
    cost: value
  }));

  return (
    <div style={{ backgroundColor: "var(--bg-surface)", borderRadius: "8px", border: "1px dashed var(--status-simulated)", padding: "var(--spacing-4)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--spacing-6)" }}>
        <h3 style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)", margin: 0 }}>Cost Simulation (Monthly)</h3>
        <span style={{ fontSize: "11px", fontWeight: 500, color: "var(--status-simulated)", backgroundColor: "color-mix(in srgb, var(--status-simulated) 15%, transparent)", padding: "2px 8px", borderRadius: "999px", textTransform: "uppercase" }}>
          Simulated — Not Live Billing Data
        </span>
      </div>
      
      <div style={{ display: "flex", gap: "var(--spacing-8)" }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "4px" }}>Total Estimated Cost</div>
          <div className="mono" style={{ fontSize: "28px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "var(--spacing-2)" }}>
            ${costResult.monthly_cost_usd?.toFixed(2) || "80.00"}
          </div>
          <div style={{ fontSize: "13px", color: "var(--text-secondary)" }}>
            {costData.reason}
          </div>
        </div>
        
        <div style={{ flex: 1, height: "140px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "var(--text-secondary)", fontFamily: "var(--font-jetbrains-mono)" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "var(--text-secondary)", fontFamily: "var(--font-jetbrains-mono)" }} axisLine={false} tickLine={false} tickFormatter={(val) => `$${val}`} />
              <Tooltip 
                cursor={{ fill: "var(--bg-surface-raised)" }}
                contentStyle={{ backgroundColor: "var(--bg-primary)", border: "1px solid var(--border)", borderRadius: "4px", fontSize: "12px" }} 
              />
              <Bar dataKey="cost" radius={[2, 2, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill="var(--status-simulated)" />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
