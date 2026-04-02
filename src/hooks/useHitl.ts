/**
 * useHitl — thin wrapper over useHITLStore for HITL queue pages.
 *
 * fetchPending is fire-and-forget (do NOT await it) — errors surface via store.error.
 * Polling is owned by App.tsx; this hook only performs a one-shot fetch on mount
 * so the page has data immediately without waiting for the next 5 s poll tick.
 * reviewed_by is intentionally omitted — no auth context in MVP.
 *
 * Coding Standard 6: one hook, one job — delegates all logic to hitlStore.
 */
import { useEffect } from "react";
import type { HITLDecisionRequest, HITLReview } from "../types/index";
import { useHITLStore } from "../store/hitlStore";

export interface UseHitlResult {
  pendingReviews: HITLReview[];
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  /** Intentional alias for store's fetchPendingReviews(). Fire-and-forget — do NOT await. */
  fetchPending: () => void;
  submitDecision: (reviewId: string, payload: HITLDecisionRequest) => Promise<void>;
}

export function useHitl(): UseHitlResult {
  const pendingReviews = useHITLStore((s) => s.pendingReviews);
  const isLoading = useHITLStore((s) => s.isLoading);
  const isSubmitting = useHITLStore((s) => s.isSubmitting);
  const error = useHITLStore((s) => s.error);
  const fetchPendingReviews = useHITLStore((s) => s.fetchPendingReviews);
  const submitDecisionStore = useHITLStore((s) => s.submitDecision);

  // One-shot fetch on mount — [] is intentional; polling is already running in App.tsx.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchPendingReviews(); }, []);

  function fetchPending(): void {
    fetchPendingReviews();
  }

  function submitDecision(
    reviewId: string,
    payload: HITLDecisionRequest
  ): Promise<void> {
    return submitDecisionStore(reviewId, payload);
  }

  return { pendingReviews, isLoading, isSubmitting, error, fetchPending, submitDecision };
}
