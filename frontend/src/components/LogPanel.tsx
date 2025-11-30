import React, { useMemo, useRef, useEffect, useState } from "react";

export type LogEvent = {
  type: string;
  timestamp: string;
  project_id: string;
  agent?: string;
  level: string;
  msg: string;
  artifact_path?: string;
};

type Props = {
  events: LogEvent[];
};

const LogPanel: React.FC<Props> = ({ events }) => {
  const [agentFilter, setAgentFilter] = useState<string>("all");
  const [levelFilter, setLevelFilter] = useState<string>("all");
  const containerRef = useRef<HTMLDivElement | null>(null);

  const filtered = useMemo(
    () =>
      events.filter(
        (event) =>
          (agentFilter === "all" || event.agent === agentFilter) &&
          (levelFilter === "all" || event.level === levelFilter),
      ),
    [events, agentFilter, levelFilter],
  );

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [filtered]);

  const agents = Array.from(new Set(events.map((event) => event.agent).filter(Boolean)));
  const levels = Array.from(new Set(events.map((event) => event.level)));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
        <select 
          value={agentFilter} 
          onChange={(event) => setAgentFilter(event.target.value)}
          style={{ fontSize: "0.8rem", padding: "2px" }}
        >
          <option value="all">All agents</option>
          {agents.map((agent) => (
            <option key={agent} value={agent || ""}>
              {agent}
            </option>
          ))}
        </select>
        <select 
          value={levelFilter} 
          onChange={(event) => setLevelFilter(event.target.value)}
          style={{ fontSize: "0.8rem", padding: "2px" }}
        >
          <option value="all">All levels</option>
          {levels.map((level) => (
            <option key={level} value={level}>
              {level}
            </option>
          ))}
        </select>
      </div>
      <div
        ref={containerRef}
        className="glass-panel"
        style={{
          flex: 1,
          overflowY: "auto",
          fontFamily: "monospace",
          fontSize: "0.8rem",
          color: "#d4d4d4",
          padding: "0.5rem",
          borderRadius: "8px",
          border: "1px solid rgba(255,255,255,0.1)",
          background: "rgba(0,0,0,0.3)"
        }}
      >
        {filtered.map((event, i) => {
          const timestamp = event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : "—";
          const agent = event.agent || "system";
          const color = event.level === "error" ? "#ef4444" : "#60a5fa";
          return (
            <div key={`${event.timestamp}-${event.msg}-${i}`} style={{ marginBottom: "4px", lineHeight: "1.4" }}>
              <span style={{ color: "#6b7280", fontSize: '0.9em' }}>[{timestamp}]</span>{" "}
              <span style={{ color, fontWeight: "bold" }}>{event.level.toUpperCase()}</span>{" "}
              <span style={{ color: "#c084fc" }}>({agent})</span>:{" "}
              <span style={{ color: "#e5e7eb" }}>{event.msg}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LogPanel;
