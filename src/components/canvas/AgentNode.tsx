/**
 * AgentNode — canvas card representing one LLM agent step.
 *
 * Displays name, role badge, and execution status dot.
 * Has both target (input) and source (output) handles.
 * Selectable — clicking opens AgentConfigPanel (FE-06).
 * Coding Standard 6: one component, one job.
 */
import { memo } from "react";
import { Handle, Position } from "reactflow";
import type { NodeProps } from "reactflow";
import type { AgentNodeData, NodeStatus } from "../../types/canvas";

/** Colour map for execution status indicator. */
const STATUS_COLORS: Record<NodeStatus, string> = {
  idle: "#95a5a6",
  running: "#f39c12",
  done: "#2ecc71",
  error: "#e74c3c",
};

function AgentNode({ data, selected }: NodeProps<AgentNodeData>): JSX.Element {
  const statusColor: string = STATUS_COLORS[data.status];

  return (
    <div
      style={{
        minWidth: 160,
        background: selected ? "#1a3a5c" : "#16213e",
        border: `2px solid ${selected ? "#3498db" : "#0f3460"}`,
        borderRadius: 8,
        padding: "8px 12px",
        color: "#e0e0e0",
        fontSize: "0.85rem",
        cursor: "grab",
        userSelect: "none",
      }}
    >
      <Handle type="target" position={Position.Left} />

      {/* ─── Header row: name + status dot ───── */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 4,
        }}
      >
        <span style={{ fontWeight: 700, fontSize: "0.9rem" }}>
          {data.name}
        </span>
        {/* Status dot — shows runtime execution state */}
        <span
          title={data.status}
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: statusColor,
            flexShrink: 0,
          }}
        />
      </div>

      {/* ─── Role badge ───── */}
      <span
        style={{
          fontSize: "0.7rem",
          background: "#0f3460",
          borderRadius: 4,
          padding: "1px 6px",
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          opacity: 0.9,
        }}
      >
        {data.role}
      </span>

      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default memo(AgentNode);
