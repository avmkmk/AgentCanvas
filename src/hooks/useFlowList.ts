/**
 * useFlowList — fetches the paginated list of flows from the API.
 *
 * Coding Standard 6: one hook, one job.
 * Coding Standard 5: errors set to state — never swallowed silently.
 * Coding Standard 8: API response validated via shared types (FE-08).
 */
import { useCallback, useEffect, useState } from "react";
import * as api from "../services/apiClient";
import type { Flow } from "../types/index";

interface UseFlowListResult {
  flows: Flow[];
  isLoading: boolean;
  error: string | null;
  /** Re-fetch the flow list on demand. */
  refetch: () => void;
}

export function useFlowList(): UseFlowListResult {
  const [flows, setFlows] = useState<Flow[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFlows = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await api.listFlows();
      // Validate response has items array before setting state
      if (!Array.isArray(result.items)) {
        throw new Error("Invalid flow list response: items is not an array");
      }
      setFlows(result.items);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to load flows";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchFlows();
  }, [fetchFlows]);

  return { flows, isLoading, error, refetch: fetchFlows };
}
