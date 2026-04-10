/**
 * useAnalytics — thin wrapper over useAnalyticsStore.
 *
 * Performs a one-shot fetch on mount. No polling — analytics are not
 * time-critical and are refreshed on each page visit.
 * Individual selectors prevent root re-renders on unrelated store updates.
 *
 * Coding Standard 6: one hook, one job — delegates all logic to analyticsStore.
 */
import { useEffect } from "react";
import type { AgentAnalyticsSummary } from "../types/analytics";
import { useAnalyticsStore } from "../store/analyticsStore";

export interface UseAnalyticsResult {
  items: AgentAnalyticsSummary[];
  total: number;
  isLoading: boolean;
  error: string | null;
  fetchAgentStats: () => Promise<void>;
  clearError: () => void;
}

export function useAnalytics(): UseAnalyticsResult {
  // Individual selectors — prevents root re-render when unrelated store keys change
  const items = useAnalyticsStore((s) => s.items);
  const total = useAnalyticsStore((s) => s.total);
  const isLoading = useAnalyticsStore((s) => s.isLoading);
  const error = useAnalyticsStore((s) => s.error);
  const fetchAgentStats = useAnalyticsStore((s) => s.fetchAgentStats);
  const clearError = useAnalyticsStore((s) => s.clearError);

  // One-shot fetch on mount — [] is intentional
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { void fetchAgentStats(); }, []);

  return { items, total, isLoading, error, fetchAgentStats, clearError };
}
