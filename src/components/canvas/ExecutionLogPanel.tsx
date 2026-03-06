/**
 * ExecutionLogPanel — scrollable list of WebSocket execution events.
 *
 * FE-11: renders logEntries from the executionStore. Auto-scrolls to the
 * bottom when new entries arrive. Shows a placeholder when no execution
 * has been started yet.
 *
 * Coding Standard 6: one component, one job — pure presentational.
 * Coding Standard 2: ref to bottom div is cleaned up automatically by React.
 */
import { useEffect, useRef } from "react";
import type { StepLogEntry, WSEventType } from "../../types";

interface ExecutionLogPanelProps {
  entries: StepLogEntry[];
  isRunning: boolean;
}

/** Icon shown next to each event type in the log. */
const EVENT_ICONS: Record<WSEventType, string> = {
  step_started: "▶",
  step_completed: "✓",
  step_failed: "✗",
  hitl_required: "⏸",
  execution_completed: "✅",
  execution_failed: "❌",
};

/** Background tint for event rows. */
const EVENT_COLORS: Partial<Record<WSEventType, string>> = {
  step_failed: "rgba(231, 76, 60, 0.08)",
  execution_failed: "rgba(231, 76, 60, 0.08)",
  execution_completed: "rgba(46, 204, 113, 0.08)",
};

export function ExecutionLogPanel({
  entries,
  isRunning,
}: ExecutionLogPanelProps): JSX.Element {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest entry when entries change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries]);

  return (
    <div
      style={{
        background: "#0d1b2a",
        borderTop: "1px solid #0f3460",
        flexShrink: 0,
        height: 180,
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
          padding: "4px 12px",
          borderBottom: "1px solid #0f3460",
          fontSize: "0.75rem",
          fontWeight: 700,
          color: "#7f8c8d",
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          flexShrink: 0,
        }}
      >
        <span>Execution Log</span>
        {isRunning && (
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "#f39c12",
              animation: "pulse 1.2s infinite",
              flexShrink: 0,
            }}
          />
        )}
      </div>

      {/* Entries */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "4px 0",
        }}
      >
        {entries.length === 0 ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              color: "#4a5568",
              fontSize: "0.8rem",
              fontStyle: "italic",
            }}
          >
            No execution yet — click Run Flow to start
          </div>
        ) : (
          entries.map((entry, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: "0.5rem",
                padding: "2px 12px",
                fontSize: "0.78rem",
                background: EVENT_COLORS[entry.event] ?? "transparent",
                fontFamily: "monospace",
              }}
            >
              <span
                style={{
                  color: "#7f8c8d",
                  flexShrink: 0,
                  fontSize: "0.7rem",
                }}
              >
                {new Date(entry.timestamp).toLocaleTimeString()}
              </span>
              <span style={{ flexShrink: 0 }}>
                {EVENT_ICONS[entry.event] ?? "·"}
              </span>
              <span style={{ color: "#b2bec3", wordBreak: "break-word" }}>
                {entry.message}
              </span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
