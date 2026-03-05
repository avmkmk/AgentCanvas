/**
 * NodePalette — left sidebar listing draggable agent role items.
 *
 * FE-04: each item sets the agent role in dataTransfer so useCanvasDrop
 * can read it on the drop event.
 * Coding Standard 6: one component, one job.
 */
import type { DragEvent } from "react";
import { DRAG_ROLE_KEY } from "../../hooks/useCanvasDrop";
import type { AgentRole } from "../../types/index";

const ROLES: AgentRole[] = [
  "researcher",
  "analyst",
  "writer",
  "critic",
  "planner",
  "custom",
];

const ROLE_COLORS: Record<AgentRole, string> = {
  researcher: "#3498db",
  analyst: "#9b59b6",
  writer: "#2ecc71",
  critic: "#e74c3c",
  planner: "#f39c12",
  custom: "#95a5a6",
};

function onDragStart(event: DragEvent<HTMLDivElement>, role: AgentRole): void {
  event.dataTransfer.setData(DRAG_ROLE_KEY, role);
  event.dataTransfer.effectAllowed = "move";
}

function NodePalette(): JSX.Element {
  return (
    <aside
      style={{
        width: "160px",
        background: "#0d1b2a",
        borderRight: "1px solid #0f3460",
        padding: "1rem 0.75rem",
        overflowY: "auto",
        flexShrink: 0,
      }}
    >
      <p
        style={{
          fontSize: "0.7rem",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: "#4a5a6a",
          marginBottom: "0.75rem",
        }}
      >
        Agent Roles
      </p>

      {ROLES.map((role) => (
        <div
          key={role}
          draggable
          onDragStart={(e) => onDragStart(e, role)}
          style={{
            padding: "6px 10px",
            marginBottom: 6,
            borderRadius: 6,
            border: `1px solid ${ROLE_COLORS[role]}`,
            color: ROLE_COLORS[role],
            fontSize: "0.8rem",
            cursor: "grab",
            userSelect: "none",
            textTransform: "capitalize",
          }}
        >
          {role}
        </div>
      ))}
    </aside>
  );
}

export default NodePalette;
