/**
 * AnalyticsPage — M5 analytics dashboard.
 *
 * Displays per-agent execution statistics from GET /analytics/agents.
 * Uses a styled HTML table (no chart library available in current stack).
 * Coding Standard 6: one component, one job. Sub-components handle rows/states.
 */
import type { AgentAnalyticsSummary } from "../types/analytics";
import { useAnalytics } from "../hooks/useAnalytics";

// ─── Sub-components ───────────────────────────────────────────────────────────

function LoadingState(): JSX.Element {
  return (
    <div style={styles.centred}>
      <p style={styles.muted}>Loading analytics…</p>
    </div>
  );
}

function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}): JSX.Element {
  return (
    <div style={styles.centred}>
      <p style={styles.error}>{message}</p>
      <button onClick={onRetry} style={styles.retryBtn}>
        Retry
      </button>
    </div>
  );
}

function EmptyState(): JSX.Element {
  return (
    <div style={styles.centred}>
      <p style={styles.muted}>No analytics data yet. Run a flow to see stats.</p>
    </div>
  );
}

function AnalyticsRow({ item }: { item: AgentAnalyticsSummary }): JSX.Element {
  const successPct = (item.success_rate * 100).toFixed(1);
  const avgMs =
    item.avg_execution_time_ms !== null
      ? `${item.avg_execution_time_ms.toFixed(0)} ms`
      : "—";
  const lastRun = item.last_executed_at
    ? new Date(item.last_executed_at).toLocaleString()
    : "—";

  return (
    <tr style={styles.row}>
      <td style={styles.cell}>{item.agent_name}</td>
      <td style={{ ...styles.cell, ...styles.num }}>{item.total_executions}</td>
      <td style={{ ...styles.cell, ...styles.num }}>{item.successful_executions}</td>
      <td style={{ ...styles.cell, ...styles.num }}>{item.failed_executions}</td>
      <td style={{ ...styles.cell, ...styles.num }}>{successPct}%</td>
      <td style={{ ...styles.cell, ...styles.num }}>{avgMs}</td>
      <td style={styles.cell}>{lastRun}</td>
    </tr>
  );
}

function AnalyticsTable({
  items,
}: {
  items: AgentAnalyticsSummary[];
}): JSX.Element {
  return (
    <div style={styles.tableWrapper}>
      <table style={styles.table}>
        <thead>
          <tr>
            {["Agent", "Total Runs", "Successful", "Failed", "Success Rate", "Avg Time", "Last Run"].map(
              (h) => (
                <th key={h} style={styles.th}>
                  {h}
                </th>
              )
            )}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <AnalyticsRow key={item.agent_id} item={item} />
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

function AnalyticsPage(): JSX.Element {
  const { items, total, isLoading, error, fetchAgentStats, clearError } =
    useAnalytics();

  function handleRetry(): void {
    clearError();
    void fetchAgentStats();
  }

  if (isLoading) return <LoadingState />;
  if (error !== null) return <ErrorState message={error} onRetry={handleRetry} />;
  if (total === 0) return <EmptyState />;

  return (
    <div style={styles.page}>
      <h2 style={styles.heading}>Agent Analytics</h2>
      <p style={styles.subheading}>{total} agent{total !== 1 ? "s" : ""}</p>
      <AnalyticsTable items={items} />
    </div>
  );
}

export default AnalyticsPage;

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = {
  page: { padding: "24px", height: "100%", overflowY: "auto" as const },
  centred: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
    gap: "12px",
  },
  heading: { margin: "0 0 4px", fontSize: "1.25rem", color: "#1a1a2e" },
  subheading: { margin: "0 0 16px", fontSize: "0.875rem", color: "#6b6b8a" },
  muted: { color: "#6b6b8a", fontSize: "1rem" },
  error: { color: "#c0392b", fontSize: "1rem" },
  retryBtn: {
    padding: "6px 16px",
    border: "1px solid #c0392b",
    borderRadius: "4px",
    background: "transparent",
    color: "#c0392b",
    cursor: "pointer",
    fontSize: "0.875rem",
  },
  tableWrapper: { overflowX: "auto" as const },
  table: {
    width: "100%",
    borderCollapse: "collapse" as const,
    fontSize: "0.875rem",
  },
  th: {
    padding: "10px 14px",
    textAlign: "left" as const,
    background: "#f0f0f8",
    color: "#4a4a6a",
    fontWeight: 600,
    borderBottom: "2px solid #ddddf0",
    whiteSpace: "nowrap" as const,
  },
  row: {},
  cell: {
    padding: "10px 14px",
    borderBottom: "1px solid #ebebf5",
    color: "#2a2a4a",
    verticalAlign: "middle" as const,
  },
  num: { textAlign: "right" as const, fontVariantNumeric: "tabular-nums" },
} as const;
