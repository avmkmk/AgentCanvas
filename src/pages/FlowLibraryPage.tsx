/**
 * FlowLibraryPage — flow list view (root route "/").
 *
 * FE-02: renders flow cards; clicking navigates to /flows/:id.
 * Uses useFlowList hook — no direct API calls in this component.
 * Coding Standard 6: one component, one job.
 */
import { Link } from "react-router-dom";
import { useFlowList } from "../hooks/useFlowList";

function FlowLibraryPage(): JSX.Element {
  const { flows, isLoading, error } = useFlowList();

  return (
    <div style={{ padding: "2rem", color: "#e0e0e0" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>
        Flow Library
      </h1>

      {error !== null && (
        <p style={{ color: "#e74c3c", marginBottom: "1rem" }}>{error}</p>
      )}

      {isLoading && flows.length === 0 && (
        <p style={{ opacity: 0.5 }}>Loading flows…</p>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: "1rem",
        }}
      >
        {flows.map((flow) => (
          <Link
            key={flow.id}
            to={`/flows/${flow.id}`}
            style={{ textDecoration: "none" }}
          >
            <div
              style={{
                background: "#16213e",
                border: "1px solid #0f3460",
                borderRadius: 8,
                padding: "1rem",
                cursor: "pointer",
                transition: "border-color 0.15s",
              }}
            >
              <p
                style={{
                  fontWeight: 700,
                  marginBottom: 4,
                  color: "#e0e0e0",
                  fontSize: "0.95rem",
                }}
              >
                {flow.name}
              </p>
              {flow.description !== null && (
                <p
                  style={{
                    fontSize: "0.8rem",
                    color: "#8a9ab0",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {flow.description}
                </p>
              )}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default FlowLibraryPage;
