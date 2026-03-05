/**
 * CanvasPage — canvas editor for a specific flow (/flows/:id).
 *
 * FE-02/FE-07: loads the flow, renders the canvas, provides a Save button.
 * Coding Standard 6: one component, one job.
 * Coding Standard 5: all async errors captured — never silent.
 */
import { useParams } from "react-router-dom";
import FlowCanvas from "../components/canvas/FlowCanvas";
import { useFlowLoad } from "../hooks/useFlowLoad";
import { useFlowSave } from "../hooks/useFlowSave";
import { useFlowStore } from "../store/flowStore";

function CanvasPage(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const { flow, nodes, edges, isLoading, error } = useFlowLoad(id);
  const { isSaving, saveError, save } = useFlowSave();
  const isDirty = useFlowStore((s) => s.isDirty);

  function handleSave(): void {
    if (id && flow) {
      void save(id, nodes, edges);
    }
  }

  if (isLoading) {
    return (
      <div style={centeredStyle}>
        <p style={{ opacity: 0.5 }}>Loading flow…</p>
      </div>
    );
  }

  if (error !== null) {
    return (
      <div style={centeredStyle}>
        <p style={{ color: "#e74c3c" }}>{error}</p>
      </div>
    );
  }

  if (flow === null) {
    return (
      <div style={centeredStyle}>
        <p style={{ opacity: 0.5 }}>Flow not found.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* ─── Toolbar ───── */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0.5rem 1rem",
          background: "#16213e",
          borderBottom: "1px solid #0f3460",
          flexShrink: 0,
        }}
      >
        <span style={{ color: "#e0e0e0", fontWeight: 700 }}>
          {flow.name}
        </span>

        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {saveError !== null && (
            <span style={{ color: "#e74c3c", fontSize: "0.8rem" }}>
              {saveError}
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={!isDirty || isSaving}
            style={{
              padding: "4px 16px",
              borderRadius: 4,
              background: isDirty ? "#3498db" : "#2c3e50",
              color: "#fff",
              border: "none",
              cursor: isDirty && !isSaving ? "pointer" : "not-allowed",
              opacity: isSaving ? 0.6 : 1,
              fontSize: "0.85rem",
            }}
          >
            {isSaving ? "Saving…" : "Save"}
          </button>
        </div>
      </div>

      {/* ─── Canvas ───── */}
      <div style={{ flex: 1, overflow: "hidden" }}>
        <FlowCanvas initialNodes={nodes} initialEdges={edges} />
      </div>
    </div>
  );
}

const centeredStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  height: "100%",
  color: "#e0e0e0",
};

export default CanvasPage;
