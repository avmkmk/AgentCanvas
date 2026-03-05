/**
 * Zustand store for Human-in-the-Loop (HITL) review queue state.
 *
 * Polling keeps the queue fresh until WebSocket push is available (M3).
 * Coding Standard 2: poll handle is always cleaned up on stopPolling.
 */
import { create } from "zustand";
import * as api from "../services/apiClient";
import type { HITLDecisionRequest, HITLReview } from "../types/index";

const POLL_INTERVAL_MS = 5_000; // 5 s — HITL is less time-critical than execution

interface HITLState {
  // ─── Data ──────────────────────────────────────────────────────────────────
  pendingReviews: HITLReview[];

  // ─── Async status ──────────────────────────────────────────────────────────
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;

  // ─── Internal: polling handle ──────────────────────────────────────────────
  _pollHandle: ReturnType<typeof setInterval> | null;

  // ─── Actions ───────────────────────────────────────────────────────────────
  fetchPendingReviews: () => Promise<void>;
  submitDecision: (
    reviewId: string,
    payload: HITLDecisionRequest
  ) => Promise<void>;
  startPolling: () => void;
  stopPolling: () => void;
  clearError: () => void;
}

export const useHITLStore = create<HITLState>()((set, get) => ({
  pendingReviews: [],
  isLoading: false,
  isSubmitting: false,
  error: null,
  _pollHandle: null,

  fetchPendingReviews: async () => {
    set({ isLoading: true, error: null });
    try {
      const reviews = await api.listPendingReviews();
      set({ pendingReviews: reviews, isLoading: false });
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load reviews";
      set({ error: message, isLoading: false });
    }
  },

  submitDecision: async (reviewId: string, payload: HITLDecisionRequest) => {
    set({ isSubmitting: true, error: null });
    try {
      const updated = await api.submitReviewDecision(reviewId, payload);
      // Remove from queue once decision is submitted
      set((state) => ({
        pendingReviews: state.pendingReviews.filter((r) => r.id !== updated.id),
        isSubmitting: false,
      }));
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to submit decision";
      set({ error: message, isSubmitting: false });
      throw err;
    }
  },

  startPolling: () => {
    // Guard: do not start a second interval if one is already running
    if (get()._pollHandle !== null) {
      return;
    }
    const handle = setInterval(() => {
      get().fetchPendingReviews();
    }, POLL_INTERVAL_MS);
    set({ _pollHandle: handle });
  },

  stopPolling: () => {
    const handle = get()._pollHandle;
    if (handle !== null) {
      clearInterval(handle);
      set({ _pollHandle: null });
    }
  },

  clearError: () => set({ error: null }),
}));
