import React, { useMemo } from "react";

export type FileEntry = {
  path: string;
  is_dir: boolean;
  size_bytes: number;
};

type TreeNode = {
  name: string;
  path: string;
  isDir: boolean;
  children: TreeNode[];
};

type Props = {
  files: FileEntry[];
  selectedPath?: string | null;
  onSelect: (path: string) => void;
  version: number;
  onVersionChange: (next: number) => void;
  onRefresh?: () => void;
};

function buildTree(entries: FileEntry[]): TreeNode[] {
  const root: TreeNode = { name: "", path: "", isDir: true, children: [] };
  for (const entry of entries) {
    const segments = entry.path.split("/").filter(Boolean);
    let current = root;
    segments.forEach((segment, index) => {
      const partialPath = segments.slice(0, index + 1).join("/");
      let child = current.children.find((node) => node.name === segment);
      if (!child) {
        child = {
          name: segment,
          path: partialPath,
          isDir: index < segments.length - 1 || entry.is_dir,
          children: [],
        };
        current.children.push(child);
      }
      current = child;
    });
  }
  return root.children;
}

const getFileIcon = (filename: string): string => {
  if (filename.endsWith(".py")) return "🐍";
  if (filename.endsWith(".js")) return "📜";
  if (filename.endsWith(".ts") || filename.endsWith(".tsx")) return "🔷";
  if (filename.endsWith(".css")) return "🎨";
  if (filename.endsWith(".html")) return "🌐";
  if (filename.endsWith(".json")) return "📋";
  if (filename.endsWith(".md")) return "📝";
  if (filename === "Makefile") return "🛠️";
  return "📄";
};

const FileTree: React.FC<Props> = ({
  files,
  selectedPath,
  onSelect,
  version,
  onVersionChange,
  onRefresh,
}) => {
  const tree = useMemo(() => buildTree(files), [files]);

  const renderNode = (node: TreeNode) => {
    if (node.isDir) {
      return (
        <li key={node.path}>
          <details open>
            <summary style={{ cursor: "pointer", color: "#9ca3af", userSelect: "none" }}>
              <span style={{ marginRight: "4px" }}>📂</span>
              {node.name || "root"}
            </summary>
            <ul style={{ paddingLeft: "1rem", borderLeft: "1px solid rgba(255,255,255,0.1)", marginLeft: "4px" }}>
              {node.children.map((child) => renderNode(child))}
            </ul>
          </details>
        </li>
      );
    }
    
    const icon = getFileIcon(node.name);
    
    return (
      <li key={node.path} style={{ margin: "2px 0" }}>
        <button
          type="button"
          onClick={() => onSelect(node.path)}
          style={{
            background: selectedPath === node.path ? "rgba(59, 130, 246, 0.2)" : "transparent",
            color: selectedPath === node.path ? "#60a5fa" : "#d1d5db",
            border: "none",
            cursor: "pointer",
            textAlign: "left",
            width: "100%",
            padding: "4px 8px",
            borderRadius: "4px",
            fontSize: "0.9rem",
            display: "flex",
            alignItems: "center",
            gap: "6px",
            transition: "all 0.2s"
          }}
        >
          <span>{icon}</span>
          <span>{node.name}</span>
        </button>
      </li>
    );
  };

  return (
    <div className="glass-panel" style={{ padding: "1rem", height: "100%", overflowY: "auto", borderRadius: 0, borderLeft: 'none', borderTop: 'none', borderBottom: 'none' }}>
      <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginBottom: "1rem" }}>
        <h3 style={{ margin: 0, fontSize: "0.9rem", color: "#e5e7eb", flex: 1, textTransform: "uppercase", letterSpacing: "1px", opacity: 0.7 }}>Files</h3>
        <label style={{ fontSize: "0.8rem", color: "#9ca3af", display: "flex", alignItems: "center" }}>
          v
          <input
            type="number"
            min={1}
            value={version}
            onChange={(event) => onVersionChange(Number(event.target.value))}
            style={{ width: "2.5rem", marginLeft: "4px", padding: "2px", background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.2)", color: "white", borderRadius: "3px" }}
          />
        </label>
        <button 
          type="button" 
          onClick={() => onRefresh?.()} 
          style={{ padding: "4px 8px", fontSize: "0.8rem", background: "rgba(0,0,0,0.3)", border: "1px solid rgba(255,255,255,0.2)", color: "white", borderRadius: "3px", cursor: "pointer" }}
          title="Refresh Files"
        >
          ↻
        </button>
      </div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {tree.map((node) => renderNode(node))}
      </ul>
    </div>
  );
};

export default FileTree;
