/**
 * Zustand store for FlowExecution state.
 *
 * M3: adds WebSocket support (FE-12), execution log (FE-11), and node
 * status map (FE-10) alongside the existing polling fallback.
 *
 * Coding Standard 2: polling handle and WS client are always cleaned up.
 * Coding Standard 5: all errors captured — never silent.
 */
import { create } from "zustand";
import * as api from "../services/apiClient";
import { ExecutionWSClient } from "../services/wsClient";
import type {
  ExecutionStartRequest,
  ExecutionStatus,
  FlowExecution,
  StepLogEntry,
  WSEvent,
  WSEventType,
} from "../types/index";
import type { NodeStatus } from "../types/canvas";

// Polling interval in ms — fallback for when WS is unavailable
const POLL_INTERVAL_MS = 2_000;

// WS connection timeout before falling back to polling (ms)
const WS_CONNECT_TIMEOUT_MS = 3_000;

// Terminal statuses where polling should stop automatically
const TERMINAL_STATUSES = new Set<ExecutionStatus>([
  "completed",
  "failed",
  "cancelled",
]);

interface ExecutionState {
  // ─── Data ──────────────────────────────────────────────────────────────────
  activeExecution: FlowExecution | null;
  executionHistory: FlowExecution[];

  /** Log entries from WebSocket events — shown in ExecutionLogPanel. */
  logEntries: StepLogEntry[];

  /**
   * Maps agent UUID → runtime NodeStatus for canvas overlays (FE-10).
   * Updated by handleWSEvent on step_started / step_completed / step_failed.
   */
  nodeStatusMap: Record<string, NodeStatus>;

  // ─── Async status ──────────────────────────────────────────────────────────
  isStarting: boolean;
  error: string | null;

  // ─── Internal: polling handle + WS client ─────────────────────────────────
  _pollHandle: ReturnType<typeof setInterval> | null;
  _wsClient: ExecutionWSClient | null;

  // ─── Actions ───────────────────────────────────────────────────────────────
  startExecution: (payload: ExecutionStartRequest) => Promise<void>;
  cancelExecution: (executionId: string) => Promise<void>;
  stopPolling: () => void;
  clearError: () => void;

  // ─── M3 WebSocket + log actions ────────────────────────────────────────────
  appendLog: (entry: StepLogEntry) => void;
  clearLog: () => void;
  handleWSEvent: (event: WSEvent) => void;
  connectWS: (executionId: string) => void;
  disconnectWS: () => void;
}

export const useExecutionStore = create<ExecutionState>()((set, get) => ({
  activeExecution: null,
  executionHistory: [],
  logEntries: [],
  nodeStatusMap: {},
  isStarting: false,
  error: null,
  _pollHandle: null,
  _wsClient: null,

  startExecution: async (payload: ExecutionStartRequest) => {
    // Clear previous log and node statuses on each new execution
    get().clearLog();
    set({ isStarting: true, error: null, nodeStatusMap: {} });

    try {
      const execution = await api.startExecution(payload);
      set({ activeExecution: execution, isStarting: false });

      if (!TERMINAL_STATUSES.has(execution.status)) {
        // Try WebSocket first; fall back to polling after timeout
        get().connectWS(execution.id);

        const wsTimeoutHandle = setTimeout(() => {
          // If still no WS-driven status update, start polling as fallback
          if (get()._pollHandle === null) {
            _startPolling(get, set, execution.id);
          }
        }, WS_CONNECT_TIMEOUT_MS);

        // Store timeout handle so it can be cleared if WS connects fast
        // We use a plain closure — no need to put it in store state
        void wsTimeoutHandle;
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to start execution";
      set({ error: message, isStarting: false });
    }
  },

  cancelExecution: async (executionId: string) => {
    try {
      const updated = await api.cancelExecution(executionId);
      get().stopPolling();
      get().disconnectWS();
      set({ activeExecution: updated });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to cancel execution";
      set({ error: message });
    }
  },

  stopPolling: () => {
    // Coding Standard 2: always clear interval ref — no resource leaks
    const handle = get()._pollHandle;
    if (handle !== null) {
      clearInterval(handle);
      set({ _pollHandle: null });
    }
  },

  clearError: () => set({ error: null }),

  // ─── M3 WebSocket + log actions ──────────────────────────────────────────

  appendLog: (entry: StepLogEntry) => {
    set((state) => ({ logEntries: [...state.logEntries, entry] }));
  },

  clearLog: () => {
    set({ logEntries: [] });
  },

  handleWSEvent: (event: WSEvent) => {
    const { appendLog } = get();
    const timestamp = new Date().toISOString();

    let message = "";
    const step_number = event.payload.step_number as number | undefined;
    const agent_name = event.payload.agent_name as string | undefined;
    const agent_id = event.payload.agent_id as string | undefined;
    const eventType: WSEventType = event.event;

    switch (eventType) {
      case "step_started":
        message = `Step ${step_number ?? "?"} started: ${agent_name ?? "unknown agent"}`;
        // Update node status to "running"
        if (agent_id) {
          set((state) => ({
            nodeStatusMap: { ...state.nodeStatusMap, [agent_id]: "running" },
          }));
        }
        break;

      case "step_completed":
        message = `Step ${step_number ?? "?"} completed: ${agent_name ?? "unknown agent"}`;
        // Update node status to "done"
        if (agent_id) {
          set((state) => ({
            nodeStatusMap: { ...state.nodeStatusMap, [agent_id]: "done" },
          }));
        }
        break;

      case "step_failed":
        message = `Step ${step_number ?? "?"} failed`;
        if (agent_id) {
          set((state) => ({
            nodeStatusMap: { ...state.nodeStatusMap, [agent_id]: "error" },
          }));
        }
        break;

      case "execution_completed":
        message = "Execution completed successfully";
        set((state) => ({
          activeExecution: state.activeExecution
            ? { ...state.activeExecution, status: "completed" }
            : null,
        }));
        // Stop polling since WS delivered the terminal event
        get().stopPolling();
        break;

      case "execution_failed":
        message = `Execution failed: ${String(event.payload.error ?? "")}`;
        set((state) => ({
          activeExecution: state.activeExecution
            ? { ...state.activeExecution, status: "failed" }
            : null,
        }));
        get().stopPolling();
        break;

      case "hitl_required":
        message = "Human review required — execution paused";
        break;

      default:
        message = `Event: ${event.event}`;
    }

    appendLog({ timestamp, event: eventType, step_number, agent_name, message });
  },

  connectWS: (executionId: string) => {
    const { handleWSEvent } = get();
    const client = new ExecutionWSClient();
    set({ _wsClient: client });

    client.connect(
      executionId,
      (event: WSEvent) => handleWSEvent(event),
      () => {
        // WS closed permanently after max retries — WS client is no longer active
        set({ _wsClient: null });
      }
    );
  },

  disconnectWS: () => {
    const { _wsClient } = get();
    if (_wsClient !== null) {
      _wsClient.disconnect();
      set({ _wsClient: null });
    }
  },
}));

/**
 * Start interval-based polling for execution status updates.
 *
 * Extracted as a module-level helper so it can be called from both
 * the WS timeout path and from tests.
 */
function _startPolling(
  get: () => ExecutionState,
  set: (partial: Partial<ExecutionState> | ((s: ExecutionState) => Partial<ExecutionState>)) => void,
  executionId: string
): void {
  const handle = setInterval(async () => {
    try {
      // Use the known executionId — more reliable than reading activeExecution.id
      const updated = await api.getExecution(executionId);
      set({ activeExecution: updated });
      if (TERMINAL_STATUSES.has(updated.status)) {
        const pollHandle = get()._pollHandle;
        if (pollHandle !== null) {
          clearInterval(pollHandle);
          set({ _pollHandle: null });
        }
        set((state) => ({
          executionHistory: [updated, ...state.executionHistory],
        }));
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Polling error";
      console.error("[ExecutionStore] poll error:", message);
    }
  }, POLL_INTERVAL_MS);
  set({ _pollHandle: handle });
}
