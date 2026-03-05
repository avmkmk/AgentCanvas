/**
 * AgentCanvas — root application component.
 *
 * MVP layout: top nav + two-column main area.
 * Left panel: flow list sidebar + HITL queue badge.
 * Right panel: React Flow canvas (placeholder for M2).
 *
 * Coding Standard 6: one component, one job.
 * State is read from Zustand stores, not local useState.
 */
import { useEffect } from "react";
import { useFlowStore } from "./store/flowStore";
import { useHITLStore } from "./store/hitlStore";

function App(): JSX.Element {
  const { flows, selectedFlow, isLoading, error, fetchFlows, selectFlow } =
    useFlowStore();
  const { pendingReviews, startPolling, stopPolling } = useHITLStore();

  // Fetch flows and start HITL polling on mount
  useEffect(() => {
    fetchFlows();
    startPolling();
    // Stop polling on unmount — Coding Standard 2: no resource leaks
    return () => stopPolling();
  }, [fetchFlows, startPolling, stopPolling]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* ─── Top navigation ─────────────────────────────────────────────── */}
      <header
        style={{
          padding: "0 1.5rem",
          height: "56px",
          background: "#1a1a2e",
          color: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexShrink: 0,
        }}
      >
        <span style={{ fontWeight: 700, fontSize: "1.1rem" }}>
          AgentCanvas
        </span>
        <span style={{ fontSize: "0.85rem", opacity: 0.7 }}>
          HITL queue:{" "}
          <strong style={{ color: pendingReviews.length > 0 ? "#ff6b6b" : "#69db7c" }}>
            {pendingReviews.length}
          </strong>{" "}
          pending
        </span>
      </header>

      {/* ─── Main area ───────────────────────────────────────────────────── */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        {/* ─── Flow sidebar ─────────────────────────────────────────────── */}
        <aside
          style={{
            width: "260px",
            background: "#16213e",
            color: "#e0e0e0",
            overflowY: "auto",
            borderRight: "1px solid #0f3460",
            flexShrink: 0,
            padding: "1rem",
          }}
        >
          <h2 style={{ fontSize: "0.85rem", textTransform: "uppercase", opacity: 0.6, marginBottom: "0.75rem" }}>
            Flows
          </h2>

          {error !== null && (
            <p style={{ color: "#ff6b6b", fontSize: "0.8rem" }}>{error}</p>
          )}

          {isLoading && flows.length === 0 && (
            <p style={{ opacity: 0.5, fontSize: "0.85rem" }}>Loading…</p>
          )}

          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {flows.map((flow) => (
              <li
                key={flow.id}
                onClick={() => { void selectFlow(flow.id); }}
                style={{
                  padding: "0.5rem 0.75rem",
                  borderRadius: "6px",
                  cursor: "pointer",
                  background:
                    selectedFlow?.id === flow.id ? "#0f3460" : "transparent",
                  marginBottom: "4px",
                  fontSize: "0.9rem",
                }}
              >
                {flow.name}
              </li>
            ))}
          </ul>
        </aside>

        {/* ─── Canvas area (React Flow — M2) ───────────────────────────── */}
        <main
          style={{
            flex: 1,
            background: "#0d0d1a",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#4a4a6a",
          }}
        >
          {selectedFlow === null ? (
            <p style={{ fontSize: "1rem" }}>
              Select a flow from the sidebar to open the canvas.
            </p>
          ) : (
            <p style={{ fontSize: "1rem" }}>
              Canvas for <strong style={{ color: "#e0e0e0" }}>{selectedFlow.name}</strong> — React Flow coming in M2.
            </p>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
