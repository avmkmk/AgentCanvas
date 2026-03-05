/**
 * StartNode — fixed entry-point node for the canvas.
 *
 * Always present; cannot be deleted (deletable: false set by FlowCanvas).
 * Only has a source handle — flow starts here.
 * Coding Standard 6: one component, one job.
 */
import { memo } from "react";
import { Handle, Position } from "reactflow";
import type { NodeProps } from "reactflow";
import type { StartNodeData } from "../../types/canvas";

function StartNode(_props: NodeProps<StartNodeData>): JSX.Element {
  return (
    <div
      style={{
        width: 60,
        height: 60,
        borderRadius: "50%",
        background: "#2ecc71",
        border: "3px solid #27ae60",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#fff",
        fontSize: "0.7rem",
        fontWeight: 700,
        userSelect: "none",
      }}
    >
      START
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

export default memo(StartNode);
