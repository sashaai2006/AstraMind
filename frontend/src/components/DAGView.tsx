import React, { useMemo, useEffect, useState, useCallback } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
  useNodesState,
  useEdgesState,
  Position,
} from "reactflow";
import dagre from "dagre";
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
  lastEvent?: any; // EventPayload from backend
};

const statusColors: Record<string, string> = {
  pending: "#facc15", // Yellow
  running: "#60a5fa", // Blue
  failed: "#ef4444",  // Red
  done: "#4ade80",    // Green
};

const nodeWidth = 180;
const nodeHeight = 120;
const isHorizontal = false;

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = "TB") => {
  // Create a fresh graph for each layout calculation
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    if (!nodeWithPosition) {
      // Fallback if node not found in layout
      return node;
    }
    
    node.targetPosition = isHorizontal ? Position.Left : Position.Top;
    node.sourcePosition = isHorizontal ? Position.Right : Position.Bottom;

    // We are shifting the dagre node position (anchor=center center) to the top left
    // so it matches the React Flow node anchor point (top left).
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };

    return node;
  });

  return { nodes, edges };
};

const DAGView: React.FC<Props> = ({ steps, lastEvent }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [comms, setComms] = useState<{id: string, source: string, target: string, msg: string}[]>([]);

  // 1. Build Graph from Steps
  useEffect(() => {
    const initialNodes: Node[] = [];
    const initialEdges: Edge[] = [];

    // CEO Node
    initialNodes.push({
      id: "ceo-node",
      type: "default",
      data: { label: "👑 CEO" },
      position: { x: 0, y: 0 },
      style: {
        background: "linear-gradient(135deg, rgba(147, 51, 234, 0.9) 0%, rgba(79, 70, 229, 0.9) 100%)",
        color: "#fff",
        border: "2px solid #a855f7",
        borderRadius: "50%",
        width: 100,
        height: 100,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontWeight: "bold",
        boxShadow: "0 0 20px rgba(168, 85, 247, 0.6)",
      },
    });

    // Step Nodes
    steps.forEach((step) => {
      initialNodes.push({
        id: step.id,
        data: {
          label: (
            <div style={{ textAlign: "center" }}>
              <div style={{ fontWeight: "bold", marginBottom: 4 }}>{step.name}</div>
              <div style={{ fontSize: "0.7em", opacity: 0.8 }}>{step.agent.toUpperCase()}</div>
              <div style={{
                fontSize: "0.6em",
                marginTop: 6,
                background: statusColors[step.status] || "#555",
                color: "#000",
                padding: "2px 6px",
                borderRadius: 4,
                fontWeight: "bold"
              }}>
                {step.status.toUpperCase()}
              </div>
            </div>
          ),
        },
        position: { x: 0, y: 0 },
        style: {
          background: "rgba(30, 30, 40, 0.9)",
          color: "#eee",
          border: `1px solid ${statusColors[step.status] || "#555"}`,
          borderRadius: "12px",
          padding: "10px",
          width: nodeWidth,
          minHeight: 80,
          backdropFilter: "blur(6px)",
          boxShadow: step.status === 'running' ? "0 0 15px rgba(96, 165, 250, 0.5)" : "none",
        },
      });
    });

    // Edges: CEO -> All first steps (or parallel groups)
    // For simplicity, connect CEO to steps that don't have dependencies (first in list usually)
    // But we need a better logic. Let's just connect CEO -> Group 1 -> Group 2...
    
    // Group steps by parallel group or ID
    const groups: Map<string, Step[]> = new Map();
    steps.forEach((step) => {
      const key = step.parallel_group || step.id;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key)!.push(step);
    });
    
    const groupKeys = Array.from(groups.keys());
    
    // Connect CEO to first group
    if (groupKeys.length > 0) {
        groups.get(groupKeys[0])!.forEach(step => {
            initialEdges.push({
                id: `ceo-${step.id}`,
                source: "ceo-node",
                target: step.id,
                type: "smoothstep",
                animated: true,
                style: { stroke: "#a855f7", strokeWidth: 2 },
            });
        });
    }

    // Connect groups sequentially
    for (let i = 0; i < groupKeys.length - 1; i++) {
        const currentSteps = groups.get(groupKeys[i])!;
        const nextSteps = groups.get(groupKeys[i+1])!;
        
        currentSteps.forEach(src => {
            nextSteps.forEach(dst => {
                initialEdges.push({
                    id: `${src.id}-${dst.id}`,
                    source: src.id,
                    target: dst.id,
                    type: "smoothstep",
                    animated: src.status === 'done' || src.status === 'running',
                    style: { stroke: "#555", strokeWidth: 1 },
                    markerEnd: { type: MarkerType.ArrowClosed, color: "#555" }
                });
            });
        });
    }

    const layouted = getLayoutedElements(initialNodes, initialEdges);
    setNodes(layouted.nodes);
    setEdges(layouted.edges);

  }, [steps, setNodes, setEdges]);

  // 2. Handle Communication Events
  useEffect(() => {
    if (!lastEvent || !lastEvent.data) return;
    if (lastEvent.data.type === "communication") {
        const { source, target, message } = lastEvent.data;
        
        // Find node IDs by name (fuzzy match)
        const sourceNode = nodes.find(n => n.data?.label?.props?.children?.[0]?.props?.children?.includes(source) || n.data?.label === source);
        const targetNode = nodes.find(n => n.data?.label?.props?.children?.[0]?.props?.children?.includes(target) || n.data?.label === target);
        
        // Fallback: if source is "ceo", use "ceo-node"
        const srcId = source === "ceo" ? "ceo-node" : (sourceNode?.id || steps.find(s => s.name === source)?.id);
        const dstId = target === "ceo" ? "ceo-node" : (targetNode?.id || steps.find(s => s.name === target)?.id);

        if (srcId && dstId) {
            const commId = `comm-${Date.now()}`;
            
            // Add temporary edge
            const newEdge: Edge = {
                id: commId,
                source: srcId,
                target: dstId,
                animated: true,
                style: { stroke: "#fbbf24", strokeWidth: 3, strokeDasharray: "5,5", animation: "dashdraw 0.5s linear infinite" },
                label: "📨 " + message,
                labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 12 },
                labelBgStyle: { fill: "rgba(0,0,0,0.7)" },
            };
            
            setEdges((eds) => [...eds, newEdge]);
            
            // Remove after 3 seconds
            setTimeout(() => {
                setEdges((eds) => eds.filter((e) => e.id !== commId));
            }, 3000);
        }
    }
  }, [lastEvent, nodes, steps, setEdges]);

  return (
    <div style={{ height: "100%", minHeight: "400px", borderRadius: "8px", overflow: 'hidden', background: 'transparent', position: 'relative' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
      >
        <Background color="#444" gap={20} size={1} />
        <Controls />
        <MiniMap nodeColor="#555" maskColor="rgba(0,0,0,0.2)" style={{background: 'transparent', border: '1px solid #333'}} />
      </ReactFlow>
      <style jsx global>{`
        @keyframes dashdraw {
          from { stroke-dashoffset: 10; }
          to { stroke-dashoffset: 0; }
        }
      `}</style>
    </div>
  );
};

export default DAGView;
