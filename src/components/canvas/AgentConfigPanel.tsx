/**
 * AgentConfigPanel — right sidebar for editing the selected AgentNode.
 *
 * FE-06: appears when an AgentNode is selected; fields: name, role,
 * system_prompt, model_name. Changes update node data and mark the
 * canvas as dirty (isDirty=true) so Save triggers a PATCH.
 *
 * Coding Standard 3: explicit types; no any.
 * Coding Standard 6: one component, one job.
 */
import type { ChangeEvent } from "react";
import type { Node } from "reactflow";
import { useFlowStore } from "../../store/flowStore";
import type { AgentNodeData } from "../../types/canvas";
import type { AgentRole } from "../../types/index";

const ROLES: AgentRole[] = [
  "researcher",
  "analyst",
  "writer",
  "critic",
  "planner",
  "custom",
];

interface AgentConfigPanelProps {
  node: Node<AgentNodeData>;
  onUpdateNode: (id: string, data: Partial<AgentNodeData>) => void;
}

function AgentConfigPanel({
  node,
  onUpdateNode,
}: AgentConfigPanelProps): JSX.Element {
  const setIsDirty = useFlowStore((s) => s.setIsDirty);

  function handleChange(
    field: keyof AgentNodeData,
    value: string
  ): void {
    onUpdateNode(node.id, { [field]: value });
    // Mark unsaved changes — FE-07 uses isDirty to enable the Save button
    setIsDirty(true);
  }

  const d = node.data;

  return (
    <aside
      style={{
        width: "260px",
        background: "#0d1b2a",
        borderLeft: "1px solid #0f3460",
        padding: "1rem",
        overflowY: "auto",
        flexShrink: 0,
        color: "#e0e0e0",
      }}
    >
      <p
        style={{
          fontSize: "0.7rem",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: "#4a5a6a",
          marginBottom: "1rem",
        }}
      >
        Agent Config
      </p>

      {/* ─── Name ───── */}
      <label style={labelStyle}>Name</label>
      <input
        style={inputStyle}
        value={d.name}
        onChange={(e: ChangeEvent<HTMLInputElement>) =>
          handleChange("name", e.target.value)
        }
      />

      {/* ─── Role ───── */}
      <label style={labelStyle}>Role</label>
      <select
        style={inputStyle}
        value={d.role}
        onChange={(e: ChangeEvent<HTMLSelectElement>) =>
          handleChange("role", e.target.value)
        }
      >
        {ROLES.map((r) => (
          <option key={r} value={r}>
            {r}
          </option>
        ))}
      </select>

      {/* ─── Model ───── */}
      <label style={labelStyle}>Model</label>
      <input
        style={inputStyle}
        value={d.model_name}
        onChange={(e: ChangeEvent<HTMLInputElement>) =>
          handleChange("model_name", e.target.value)
        }
      />

      {/* ─── System Prompt ───── */}
      <label style={labelStyle}>System Prompt</label>
      <textarea
        style={{ ...inputStyle, height: 160, resize: "vertical" }}
        value={d.system_prompt}
        onChange={(e: ChangeEvent<HTMLTextAreaElement>) =>
          handleChange("system_prompt", e.target.value)
        }
      />
    </aside>
  );
}

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: "0.75rem",
  color: "#8a9ab0",
  marginBottom: 4,
  marginTop: 12,
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  background: "#16213e",
  border: "1px solid #0f3460",
  borderRadius: 4,
  color: "#e0e0e0",
  padding: "4px 8px",
  fontSize: "0.85rem",
  boxSizing: "border-box",
};

export default AgentConfigPanel;
