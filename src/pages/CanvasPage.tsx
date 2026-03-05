/**
 * CanvasPage — canvas editor for a specific flow (/flows/:id).
 *
 * FE-02/FE-07: loads the flow, renders the canvas, provides a Save button.
 * FE-09 (M3): Run Flow button in the toolbar.
 * FE-10 (M3): passes nodeStatusMap to FlowCanvas for execution overlays.
 * FE-12 (M3): mounts WebSocket connection for execution events; shows log panel.
 *
 * Coding Standard 6: one component, one job.
 * Coding Standard 5: all async errors captured — never silent.
 */
import { useParams } from "react-router-dom";
import { ExecutionLogPanel } from "../components/canvas/ExecutionLogPanel";
import FlowCanvas from "../components/canvas/FlowCanvas";
import { RunButton } from "../components/canvas/RunButton";
import { useWebSocket } from "../hooks/useWebSocket";
import { useFlowLoad } from "../hooks/useFlowLoad";
import { useFlowSave } from "../hooks/useFlowSave";
import { useExecutionStore } from "../store/executionStore";
import { useFlowStore } from "../store/flowStore";

function CanvasPage(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  const { flow, nodes, edges, isLoading, error } = useFlowLoad(id);
  const { isSaving, saveError, save } = useFlowSave();
  const isDirty = useFlowStore((s) => s.isDirty);

  // M3: execution state
  const activeExecution = useExecutionStore((s) => s.activeExecution);
  const logEntries = useExecutionStore((s) => s.logEntries);
  const nodeStatusMap = useExecutionStore((s) => s.nodeStatusMap);
  const isRunning =
    activeExecution?.status === "running" ||
    activeExecution?.status === "pending";

  // M3: mount WebSocket connection when an execution is active (FE-12)
  useWebSocket(activeExecution?.id ?? null);

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

          {/* M3: Run Flow button — FE-09 */}
          {id !== undefined && <RunButton flowId={id} />}
        </div>
      </div>

      {/* ─── Canvas ───── */}
      <div style={{ flex: 1, overflow: "hidden" }}>
        {/* FE-10: pass nodeStatusMap for execution overlays */}
        <FlowCanvas
          initialNodes={nodes}
          initialEdges={edges}
          nodeStatusMap={nodeStatusMap}
        />
      </div>

      {/* ─── Execution Log Panel — FE-11/FE-12 ───── */}
      <ExecutionLogPanel entries={logEntries} isRunning={isRunning} />
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
