import React, { useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
} from "reactflow";
import "reactflow/dist/style.css";

export type Step = {
  id: string;
  name: string;
  agent: string;
  status: string;
  parallel_group?: string | null;
};

type Props = {
  steps: Step[];
};

const statusColors: Record<string, string> = {
  pending: "#facc15", // Yellow
  running: "#60a5fa", // Blue
  failed: "#ef4444",  // Red
  done: "#4ade80",    // Green
};

const statusGlows: Record<string, string> = {
  pending: "0 0 15px rgba(250, 204, 21, 0.6)",
  running: "0 0 20px rgba(96, 165, 250, 0.8)",
  failed: "0 0 20px rgba(239, 68, 68, 0.8)",
  done: "0 0 15px rgba(74, 222, 128, 0.6)",
};

const DAGView: React.FC<Props> = ({ steps }) => {
  const nodes: Node[] = useMemo(
    () =>
      steps.map((step, index) => ({
        id: step.id,
        data: { label: (
            <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.1em', fontWeight: 'bold', marginBottom: '4px' }}>{step.name}</div>
                <div style={{ fontSize: '0.8em', opacity: 0.8 }}>{step.agent}</div>
            </div>
        ) },
        position: { x: (index % 3) * 300 + 50, y: Math.floor(index / 3) * 200 + 50 },
        style: {
          background: "rgba(20, 20, 35, 0.85)",
          backdropFilter: "blur(5px)",
          color: "#e0e0e0",
          border: `2px solid ${statusColors[step.status] || "#555"}`,
          padding: "1rem",
          borderRadius: "50%", // Planets!
          width: 140,
          height: 140,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: statusGlows[step.status] || "none",
          transition: "all 0.3s ease",
        },
      })),
    [steps],
  );

  const edges: Edge[] = useMemo(() => {
    const result: Edge[] = [];
    for (let i = 0; i < steps.length - 1; i += 1) {
      result.push({
        id: `${steps[i].id}->${steps[i + 1].id}`,
        source: steps[i].id,
        target: steps[i + 1].id,
        animated: true, // Always animate for energy flow feel
        style: { stroke: "#60a5fa", strokeWidth: 2, filter: "drop-shadow(0 0 3px #60a5fa)" },
        type: "smoothstep",
        markerEnd: {
            type: MarkerType.ArrowClosed,
            color: "#60a5fa",
        },
      });
    }
    return result;
  }, [steps]);

  return (
    <div style={{ height: "100%", minHeight: "400px", background: "transparent", borderRadius: "8px", overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <MiniMap 
            style={{ background: "rgba(0,0,0,0.5)", border: "1px solid #333" }} 
            nodeColor={(n) => {
                // Helper to extract border color from style to use in minimap
                const style = n.style as any;
                return style?.borderColor || "#555";
            }}
        />
        <Controls style={{ buttonBg: "#222", buttonColor: "#eee", buttonBorder: "1px solid #444" }} />
        <Background color="#444" gap={20} size={1} style={{ opacity: 0.3 }} />
      </ReactFlow>
    </div>
  );
};

export default DAGView;
