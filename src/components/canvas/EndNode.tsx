/**
 * EndNode — fixed exit-point node for the canvas.
 *
 * Always present; cannot be deleted (deletable: false set by FlowCanvas).
 * Only has a target handle — flow ends here.
 * Coding Standard 6: one component, one job.
 */
import { memo } from "react";
import { Handle, Position } from "reactflow";
import type { NodeProps } from "reactflow";
import type { EndNodeData } from "../../types/canvas";

function EndNode(_props: NodeProps<EndNodeData>): JSX.Element {
  return (
    <div
      style={{
        width: 60,
        height: 60,
        borderRadius: "50%",
        background: "#e74c3c",
        border: "3px solid #c0392b",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#fff",
        fontSize: "0.7rem",
        fontWeight: 700,
        userSelect: "none",
      }}
    >
      END
      <Handle type="target" position={Position.Left} />
    </div>
  );
}

export default memo(EndNode);
