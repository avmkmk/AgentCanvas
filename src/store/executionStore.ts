/**
 * Zustand store for FlowExecution state.
 *
 * Polling interval is intentionally kept short (2 s) for MVP — will be
 * replaced by WebSocket push events in M3 (issue FE-18).
 * Coding Standard 2: polling interval ref is always cleared on stop.
 */
import { create } from "zustand";
import * as api from "../services/apiClient";
import type { ExecutionStartRequest, ExecutionStatus, FlowExecution } from "../types/index";

// Polling interval in ms — constant, not configurable at runtime
const POLL_INTERVAL_MS = 2_000;

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

  // ─── Async status ──────────────────────────────────────────────────────────
  isStarting: boolean;
  error: string | null;

  // ─── Internal: polling handle ──────────────────────────────────────────────
  _pollHandle: ReturnType<typeof setInterval> | null;

  // ─── Actions ───────────────────────────────────────────────────────────────
  startExecution: (payload: ExecutionStartRequest) => Promise<void>;
  cancelExecution: (executionId: string) => Promise<void>;
  stopPolling: () => void;
  clearError: () => void;
}

export const useExecutionStore = create<ExecutionState>()((set, get) => ({
  activeExecution: null,
  executionHistory: [],
  isStarting: false,
  error: null,
  _pollHandle: null,

  startExecution: async (payload: ExecutionStartRequest) => {
    set({ isStarting: true, error: null });
    try {
      const execution = await api.startExecution(payload);
      set({ activeExecution: execution, isStarting: false });

      // Begin polling only when execution is non-terminal
      if (!TERMINAL_STATUSES.has(execution.status)) {
        const handle = setInterval(async () => {
          const current = get().activeExecution;
          if (current === null) {
            get().stopPolling();
            return;
          }
          try {
            const updated = await api.getExecution(current.id);
            set({ activeExecution: updated });
            // Auto-stop when terminal state reached
            if (TERMINAL_STATUSES.has(updated.status)) {
              get().stopPolling();
              // Archive to history
              set((state) => ({
                executionHistory: [updated, ...state.executionHistory],
              }));
            }
          } catch (err) {
            // Polling failure is non-fatal — keep trying but log
            const message =
              err instanceof Error ? err.message : "Polling error";
            console.error("[ExecutionStore] poll error:", message);
          }
        }, POLL_INTERVAL_MS);
        set({ _pollHandle: handle });
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
}));
