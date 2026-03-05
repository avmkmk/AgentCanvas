/**
 * AgentCanvas — root application component.
 *
 * FE-02: BrowserRouter wraps the app; routes delegate to page components.
 * Top nav persists across all routes and shows HITL queue badge.
 *
 * Coding Standard 6: one component, one job — routing + persistent nav only.
 * State is read from Zustand stores, not local useState.
 */
import { useEffect } from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import AnalyticsPage from "./pages/AnalyticsPage";
import CanvasPage from "./pages/CanvasPage";
import FlowLibraryPage from "./pages/FlowLibraryPage";
import { useHITLStore } from "./store/hitlStore";

function App(): JSX.Element {
  const { pendingReviews, startPolling, stopPolling } = useHITLStore();

  // Start HITL polling on mount — stop on unmount (Coding Standard 2: no resource leaks)
  useEffect(() => {
    startPolling();
    return () => stopPolling();
  }, [startPolling, stopPolling]);

  return (
    <BrowserRouter>
      <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: "#0d0d1a" }}>
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
          <Link
            to="/"
            style={{
              fontWeight: 700,
              fontSize: "1.1rem",
              color: "#fff",
              textDecoration: "none",
            }}
          >
            AgentCanvas
          </Link>

          <nav style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
            <Link to="/" style={navLinkStyle}>
              Flows
            </Link>
            <Link to="/analytics" style={navLinkStyle}>
              Analytics
            </Link>
            <span style={{ fontSize: "0.85rem", opacity: 0.7 }}>
              HITL:{" "}
              <strong
                style={{
                  color: pendingReviews.length > 0 ? "#ff6b6b" : "#69db7c",
                }}
              >
                {pendingReviews.length}
              </strong>{" "}
              pending
            </span>
          </nav>
        </header>

        {/* ─── Page content ────────────────────────────────────────────────── */}
        <main style={{ flex: 1, overflow: "hidden" }}>
          <Routes>
            <Route path="/" element={<FlowLibraryPage />} />
            <Route path="/flows/:id" element={<CanvasPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

const navLinkStyle: React.CSSProperties = {
  color: "#a0aec0",
  textDecoration: "none",
  fontSize: "0.9rem",
};

export default App;
