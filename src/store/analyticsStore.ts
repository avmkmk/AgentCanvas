/**
 * Zustand store for analytics state.
 *
 * Fetches agent analytics from GET /analytics/agents on demand.
 * No polling — analytics data is not time-critical.
 * Coding Standard 2: async state always has loading + error guards.
 */
import { create } from "zustand";
import * as api from "../services/apiClient";
import type { AgentAnalyticsSummary } from "../types/analytics";

interface AnalyticsState {
  // ─── Data ──────────────────────────────────────────────────────────────────
  items: AgentAnalyticsSummary[];
  total: number;

  // ─── Async status ──────────────────────────────────────────────────────────
  isLoading: boolean;
  error: string | null;

  // ─── Actions ───────────────────────────────────────────────────────────────
  fetchAgentStats: () => Promise<void>;
  clearError: () => void;
}

export const useAnalyticsStore = create<AnalyticsState>()((set) => ({
  items: [],
  total: 0,
  // Start as true so the loading spinner renders on first mount before
  // fetchAgentStats is called by useAnalytics — prevents a flash of EmptyState.
  isLoading: true,
  error: null,

  fetchAgentStats: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.listAgentAnalytics();
      // Validate response shape at the API boundary before entering the store.
      // Zod is not installed; guard with structural checks consistent with existing stores.
      // The apiClient interceptor normalises all non-2xx responses to Error, so
      // a successful response that fails this check means a backend schema change.
      if (!Array.isArray(response.items) || typeof response.total !== "number") {
        throw new Error("Unexpected response shape from /analytics/agents");
      }
      set({ items: response.items, total: response.total, isLoading: false });
    } catch (err) {
      // apiClient interceptor guarantees err is always an Error instance.
      // The fallback string is a safety net only.
      const message =
        err instanceof Error ? err.message : "Failed to load analytics";
      set({ error: message, isLoading: false });
    }
  },

  clearError: () => set({ error: null }),
}));
