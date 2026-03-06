/**
 * RunButton — triggers a flow execution from the canvas toolbar.
 *
 * FE-09: uses useRunFlow hook; shows loading state while the POST /executions
 * request is in flight and while status is "running".
 *
 * Coding Standard 6: one component, one job — no business logic here.
 * Coding Standard 5: error is surfaced in the UI — never silent.
 */
import { useRunFlow } from "../../hooks/useRunFlow";

interface RunButtonProps {
  /** Backend UUID of the flow to execute. */
  flowId: string;
}

export function RunButton({ flowId }: RunButtonProps): JSX.Element {
  const { run, isStarting, error, status } = useRunFlow(flowId);

  const isRunning = isStarting || status === "running";
  const label = isRunning ? "Running…" : "Run Flow";

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "0.5rem",
      }}
    >
      <button
        onClick={run}
        disabled={isRunning}
        title={error ?? undefined}
        style={{
          padding: "4px 16px",
          borderRadius: 4,
          background: isRunning ? "#2c3e50" : "#27ae60",
          color: "#fff",
          border: "none",
          cursor: isRunning ? "not-allowed" : "pointer",
          opacity: isRunning ? 0.65 : 1,
          fontSize: "0.85rem",
          fontWeight: 600,
          transition: "background 0.15s",
        }}
      >
        {label}
      </button>

      {error !== null && (
        <span
          style={{
            color: "#e74c3c",
            fontSize: "0.75rem",
            maxWidth: 200,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
          title={error}
        >
          {error}
        </span>
      )}
    </div>
  );
}
